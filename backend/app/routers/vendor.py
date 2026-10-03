from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, get_vendor
from app.models.user import User
from app.services.vendor_service import vendor_service
from app.schemas.vendor import (
    VendorProfileUpdate, VendorProfileResponse,
    VendorServiceCreate, VendorServiceUpdate, VendorServiceResponse,
    VendorPhotoCreate, VendorPhotoResponse,
    VendorAvailabilityCreate, VendorAvailabilityResponse,
    WorkingHoursCreate, WorkingHoursResponse,
    VendorListResponse, CategoryResponse, CustomCategoryRequest,VendorDocumentResponse
)
from app.services.analytics_service import analytics_service
from app.schemas.analytics import VendorAnalyticsResponse
from fastapi import UploadFile, File
from app.utils.cloudinary_client import upload_image
from typing import List
from app.schemas.compare import VendorCompareData
from app.models.customer import CustomerProfile
from app.utils.image_processing import process_image, MAX_SIZE_BYTES
import io

import tempfile
import os
from app.utils.video_processing import process_video, generate_thumbnail, ABSOLUTE_MAX_VIDEO_SIZE
from app.utils.cloudinary_client import upload_video, upload_image
from app.models.vendor import VendorVideo, VendorProfile
from app.schemas.vendor import VendorVideoResponse

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}


ABSOLUTE_MAX_SIZE = 25 * 1024 * 1024  # hard reject anything above this, even before compression

router = APIRouter(tags=["Vendors"])


# ── PUBLIC ROUTES (no auth needed) ──

@router.get("", response_model=List[VendorListResponse])
def list_vendors(
    state_id:    Optional[int] = Query(None),
    city_id:     Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    skip:        int           = Query(0),
    limit:       int           = Query(20),
    db:          Session       = Depends(get_db)
):
    return vendor_service.list_vendors(
        db, state_id, city_id, category_id, skip, limit
    )

@router.get("/compare", response_model=List[VendorCompareData])
def compare_vendors(
    ids: str = Query(..., description="Comma-separated vendor IDs, e.g. 3,7,12"),
    db: Session = Depends(get_db)
):
    try:
        vendor_ids = [int(x.strip()) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid vendor IDs format")

    return vendor_service.get_compare_data(db, vendor_ids)
@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return vendor_service.get_categories(db)

@router.get("/by-slug/{slug}", response_model=VendorProfileResponse)
def get_vendor_by_slug(slug: str, db: Session = Depends(get_db)):
    return vendor_service.get_profile_by_slug(db, slug)

@router.get("/{vendor_id}", response_model=VendorProfileResponse)
def get_vendor_detail(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    return vendor_service.get_profile_by_id(db, vendor_id)


@router.get("/{vendor_id}/services",
            response_model=List[VendorServiceResponse])
def get_vendor_services(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    return vendor_service.get_services(db, vendor_id)


@router.get("/{vendor_id}/photos",
            response_model=List[VendorPhotoResponse])
def get_vendor_photos(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    return vendor_service.get_photos(db, vendor_id)


@router.get("/{vendor_id}/availability",
            response_model=List[VendorAvailabilityResponse])
def get_vendor_availability(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    return vendor_service.get_availability(db, vendor_id)


# ── VENDOR PROTECTED ROUTES ──

@router.get("/me/profile", response_model=VendorProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.get_profile(db, current_user.id)


@router.put("/me/profile", response_model=VendorProfileResponse)
def update_my_profile(
    data: VendorProfileUpdate,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.update_profile(db, current_user.id, data)


@router.post("/me/services", response_model=VendorServiceResponse)
def add_service(
    data: VendorServiceCreate,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.add_service(db, current_user.id, data)


@router.put("/me/services/{service_id}",
            response_model=VendorServiceResponse)
def update_service(
    service_id: int,
    data: VendorServiceUpdate,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.update_service(
        db, current_user.id, service_id, data
    )


@router.delete("/me/services/{service_id}")
def delete_service(
    service_id: int,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.delete_service(
        db, current_user.id, service_id
    )


@router.post("/me/photos", response_model=VendorPhotoResponse)
def add_photo(
    data: VendorPhotoCreate,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.add_photo(db, current_user.id, data)


@router.delete("/me/photos/{photo_id}")
def delete_photo(
    photo_id: int,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.delete_photo(
        db, current_user.id, photo_id
    )


@router.post("/me/availability",
             response_model=VendorAvailabilityResponse)
def set_availability(
    data: VendorAvailabilityCreate,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.set_availability(
        db, current_user.id, data
    )


@router.post("/me/working-hours",
             response_model=WorkingHoursResponse)
def set_working_hours(
    data: WorkingHoursCreate,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.set_working_hours(
        db, current_user.id, data
    )


@router.get("/me/working-hours",
            response_model=List[WorkingHoursResponse])
def get_working_hours(
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    vendor = vendor_service.get_profile(db, current_user.id)
    return vendor_service.get_working_hours(db, vendor.id)


@router.post("/me/categories/{category_id}")
def assign_category(
    category_id: int,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.assign_category(
        db, current_user.id, category_id
    )




@router.post("/me/upload-photo")
async def upload_photo_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, or WEBP images are allowed"
        )

    file_bytes = await file.read()

    if len(file_bytes) > ABSOLUTE_MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image is too large. Please choose a file under 25MB."
        )

    # Auto-compress if over 10MB, otherwise pass through unchanged
    processed_bytes = process_image(file_bytes, file.filename)

    photo_url = upload_image(io.BytesIO(processed_bytes))
    return {"photo_url": photo_url}
@router.post("/me/categories/custom")
def request_custom_category(
    data: CustomCategoryRequest,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.request_custom_category(
        db, current_user.id, data.name, data.description
    )

@router.get("/me/approval-status")
def get_approval_status(
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    vendor = vendor_service.get_profile(db, current_user.id)
    return {
        "is_approved": vendor.is_approved,
        "rejection_reason": vendor.rejection_reason
    }

@router.get("/me/categories", response_model=List[CategoryResponse])
def get_my_categories(
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    vendor = vendor_service.get_profile(db, current_user.id)
    return vendor_service.get_vendor_categories(db, vendor.id)


@router.delete("/me/categories/{category_id}")
def remove_category(
    category_id: int,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.remove_category(db, current_user.id, category_id)



@router.post("/me/upload-document", response_model=VendorDocumentResponse)
async def upload_document(
    document_type: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    document_url = upload_image(file.file, folder="evenzoo/documents")
    return vendor_service.add_document(db, current_user.id, document_type, document_url)


@router.get("/me/documents", response_model=List[VendorDocumentResponse])
def get_my_documents(
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    vendor = vendor_service.get_profile(db, current_user.id)
    return vendor_service.get_documents(db, vendor.id)


@router.delete("/me/documents/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return vendor_service.delete_document(db, current_user.id, document_id)



@router.get("/me/analytics", response_model=VendorAnalyticsResponse)
def get_my_analytics(
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    vendor = vendor_service.get_profile(db, current_user.id)
    return analytics_service.get_vendor_analytics(db, vendor.id)

@router.post("/me/upload-video", response_model=VendorVideoResponse)
async def upload_vendor_video(
    file: UploadFile = File(...),
    caption: Optional[str] = None,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=400, detail="Only MP4, MOV, or WEBM videos are allowed")

    vendor = db.query(VendorProfile).filter(VendorProfile.user_id == current_user.id).first()

    file_bytes = await file.read()
    if len(file_bytes) > ABSOLUTE_MAX_VIDEO_SIZE:
        raise HTTPException(status_code=400, detail="Video is too large. Please choose a file under 50MB.")

    # Write to a temp file since moviepy needs a real file path, not bytes in memory
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        processed_path = process_video(tmp_path)
        thumb_path = generate_thumbnail(processed_path)

        video_url = upload_video(processed_path)
        thumbnail_url = upload_image(open(thumb_path, "rb"))

        video_record = VendorVideo(
            vendor_id=vendor.id,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            caption=caption
        )
        db.add(video_record)
        db.commit()
        db.refresh(video_record)

        return video_record
    finally:
        # Clean up every temp file, whether processing succeeded or failed
        for path in {tmp_path, processed_path if 'processed_path' in dir() else None, thumb_path if 'thumb_path' in dir() else None}:
            if path and os.path.exists(path):
                os.remove(path)


@router.get("/{vendor_id}/videos", response_model=List[VendorVideoResponse])
def get_vendor_videos(vendor_id: int, db: Session = Depends(get_db)):
    return db.query(VendorVideo).filter(VendorVideo.vendor_id == vendor_id).order_by(VendorVideo.created_at.desc()).all()


@router.delete("/me/videos/{video_id}")
def delete_vendor_video(
    video_id: int,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    vendor = db.query(VendorProfile).filter(VendorProfile.user_id == current_user.id).first()
    video = db.query(VendorVideo).filter(
        VendorVideo.id == video_id,
        VendorVideo.vendor_id == vendor.id   # ← ownership check, this is the IDOR fix pattern applied here
    ).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    db.delete(video)
    db.commit()
    return {"message": "Video deleted"}

    