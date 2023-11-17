from datetime import datetime

from django.db import IntegrityError, transaction
from ninja import Field as APIField
from ninja import Router as APIRouter
from ninja import Schema, UploadedFile
from ninja.pagination import paginate
from pydantic import validator

from c3nav.api.exceptions import APIConflict, APIRequestValidationFailed, API404
from c3nav.api.newauth import BearerAuth, auth_permission_responses, auth_responses
from c3nav.mesh.dataformats import BoardType, FirmwareImage, ChipType
from c3nav.mesh.models import FirmwareVersion, FirmwareBuild

api_router = APIRouter(tags=["mesh"])


class FirmwareBuildSchema(Schema):
    id: int
    variant: str = APIField(..., example="c3uart")
    chip: ChipType = APIField(..., example=ChipType.ESP32_C3.name)
    sha256_hash: str = APIField(..., regex=r"^[0-9a-f]{64}$")
    url: str = APIField(..., alias="binary", example="/media/firmware/012345/firmware.bin")
    # todo: should not be none, but parse errors
    boards: list[BoardType] = APIField(None, example=[BoardType.C3NAV_LOCATION_PCB_REV_0_2.name, ])

    @staticmethod
    def resolve_chip(obj):
        # todo: do this in model? idk
        return ChipType(obj.chip)


class FirmwareSchema(Schema):
    id: int
    project_name: str = APIField(..., example="c3nav_positioning")
    version: str = APIField(..., example="499837d-dirty")
    idf_version: str = APIField(..., example="v5.1-476-g3187b8b326")
    created: datetime
    builds: list[FirmwareBuildSchema]

    @validator('builds')
    def builds_variants_must_be_unique(cls, builds):
        if len(set(build.variant for build in builds)) != len(builds):
            raise ValueError("builds must have unique variant identifiers")
        return builds


class Error(Schema):
    detail: str


@api_router.get('/firmwares/', summary="List available firmwares",
                response={200: list[FirmwareSchema], **auth_responses})
@paginate
def firmware_list(request):
    return FirmwareVersion.objects.all()


@api_router.get('/firmwares/{firmware_id}/', summary="Get specific firmware",
                response={200: FirmwareSchema, **API404.dict(), **auth_responses})
def firmware_detail(request, firmware_id: int):
    try:
        return FirmwareVersion.objects.get(id=firmware_id)
    except FirmwareVersion.DoesNotExist:
        raise API404("Firmware not found")


@api_router.get('/firmwares/{firmware_id}/{variant}/image_data',
                summary="Get header data of firmware build image",
                response={200: FirmwareImage.schema, **API404.dict(), **auth_responses})
def firmware_build_image(request, firmware_id: int, variant: str):
    try:
        build = FirmwareBuild.objects.get(version_id=firmware_id, variant=variant)
        return FirmwareImage.tojson(build.firmware_image)
    except FirmwareVersion.DoesNotExist:
        raise API404("Firmware or firmware build not found")


@api_router.get('/firmwares/{firmware_id}/{variant}/project_description',
                summary="Get project description of firmware build",
                response={200: dict, **API404.dict(), **auth_responses})
def firmware_project_description(request, firmware_id: int, variant: str):
    try:
        return FirmwareBuild.objects.get(version_id=firmware_id, variant=variant).firmware_description
    except FirmwareVersion.DoesNotExist:
        raise API404("Firmware or firmware build not found")


class UploadFirmwareBuildSchema(Schema):
    variant: str = APIField(..., example="c3uart")
    boards: list[BoardType] = APIField(..., example=[BoardType.C3NAV_LOCATION_PCB_REV_0_2.name, ])
    project_description: dict = APIField(..., title='project_description.json contents')
    uploaded_filename: str = APIField(..., example="firmware.bin")


class UploadFirmwareSchema(Schema):
    project_name: str = APIField(..., example="c3nav_positioning")
    version: str = APIField(..., example="499837d-dirty")
    idf_version: str = APIField(..., example="v5.1-476-g3187b8b326")
    builds: list[UploadFirmwareBuildSchema] = APIField(..., min_items=1, unique_items=True)

    @validator('builds')
    def builds_variants_must_be_unique(cls, builds):
        if len(set(build.variant for build in builds)) != len(builds):
            raise ValueError("builds must have unique variant identifiers")
        return builds


@api_router.post('/firmwares/upload', summary="Upload firmware", auth=BearerAuth(superuser=True),
                 description="your OpenAPI viewer might not show it: firmware_data is UploadFirmwareSchema as json",
                 response={200: FirmwareSchema, **auth_permission_responses, **APIConflict.dict()})
def firmware_upload(request, firmware_data: UploadFirmwareSchema, binary_files: list[UploadedFile]):
    binary_files_by_name = {binary_file.name: binary_file for binary_file in binary_files}
    if len([binary_file.name for binary_file in binary_files]) != len(binary_files_by_name):
        raise APIRequestValidationFailed("Filenames of uploaded binary files must be unique.")

    build_filenames = [build_data.uploaded_filename for build_data in firmware_data.builds]
    if len(build_filenames) != len(set(build_filenames)):
        raise APIRequestValidationFailed("Builds need to refer to different unique binary file names.")

    if set(binary_files_by_name) != set(build_filenames):
        raise APIRequestValidationFailed("All uploaded binary files need to be refered to by one build.")

    try:
        with transaction.atomic():
            version = FirmwareVersion.objects.create(
                project_name=firmware_data.project_name,
                version=firmware_data.version,
                idf_version=firmware_data.idf_version,
                uploader=request.auth,
            )

            for build_data in firmware_data.builds:
                # if bin_file.size > 4 * 1024 * 1024:
                #    raise ValueError  # todo: better error

                # h = hashlib.sha256()
                # h.update(build_data.binary)
                # sha256_bin_file = h.hexdigest()  # todo: verify sha256 correctly
                #
                # if sha256_bin_file != build_data.sha256_hash:
                #     raise ValueError

                try:
                    image = FirmwareImage.from_file(binary_files_by_name[build_data.uploaded_filename].open('rb'))
                except ValueError:
                    raise APIRequestValidationFailed(f"Can't parse binary image {build_data.uploaded_filename}")

                build = version.builds.create(
                    variant=build_data.variant,
                    chip=image.ext_header.chip.name,
                    sha256_hash=image.app_desc.app_elf_sha256,
                    project_description=build_data.project_description,
                    binary=binary_files_by_name[build_data.uploaded_filename],
                )

                for board in build_data.boards:
                    build.firmwarebuildboard_set.create(board=board.name)
    except IntegrityError:
        raise APIConflict('Firmware version already exists.')

    return version