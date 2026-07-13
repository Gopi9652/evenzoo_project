from fastapi import APIRouter, Depends, Query
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


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return vendor_service.get_categories(db)


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
    photo_url = upload_image(file.file)
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