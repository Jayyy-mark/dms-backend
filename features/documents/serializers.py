from rest_framework import serializers
from features.documents.models import Document
from features.staffs.models import Staff
from features.categories.serializers import CategorySerializer
from features.dtypes.serializers import DtypeSerializer
from features.dtypes.models import Dtype
from features.departments.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class StaffSerializer(serializers.ModelSerializer):
    department_id = serializers.IntegerField()
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    staff_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    dtype_id = serializers.IntegerField()
    staff = StaffSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    dtype = DtypeSerializer(read_only=True)

    class Meta:
        model = Document
        fields = "__all__"

    # document_id = serializers.CharField(required=True)
    # document_name = serializers.CharField(required=True)
    # document = serializers.FileField()
    # staff_id = serializers.IntegerField(required=True)
    # dtype_id = serializers.IntegerField(required=True)
    # category_id = serializers.IntegerField(required=True)
    # description = serializers.CharField(required=True)


class DocumentSearchSerializer(serializers.Serializer):
    document_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    document_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    staff_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    category_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    dtype_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    department_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    created_at = serializers.CharField(required=False)
    updated_at = serializers.CharField(required=False)
    expired_at = serializers.CharField(required=False)
    archived_at = serializers.CharField(required=False)
    recycled_at = serializers.CharField(required=False)

    from_date = serializers.CharField(required=False)
    to_date = serializers.CharField(required=False)
    updated_from_date = serializers.CharField(required=False)
    updated_to_date = serializers.CharField(required=False)
    expired_from_date = serializers.CharField(required=False)
    expired_to_date = serializers.CharField(required=False)


class DeepSearchDocumentSerializer(serializers.Serializer):

    text = serializers.CharField(
        required=True,
        allow_null=True,
        allow_blank=True,
        error_messages={
            "required": "Text is required.",
            "null": "Text cannot be null.",
            "blank": "Text cannot be empty.",
        },
    )
    category_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    department_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    document_status = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    from_date = serializers.CharField(required=False)
    to_date = serializers.CharField(required=False)
    updated_from_date = serializers.CharField(required=False)
    updated_to_date = serializers.CharField(required=False)


class DocumentUpdateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(required=False, allow_null=True)
    dtype_id = serializers.IntegerField(required=False, allow_null=True)
    staff_id = serializers.IntegerField(required=False, allow_null=True)
    expired_at = serializers.DateField(required=False, allow_null=True)
    document = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Document
        fields = [
            "document_id",
            "document_name",
            "staff_id",
            "category_id",
            "dtype_id",
            "description",
            "expired_at",
            "document",
        ]

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, "copy") else dict(data)
        if "dtype" in data and "dtype_id" not in data:
            data["dtype_id"] = data["dtype"]
        if "category" in data and "category_id" not in data:
            data["category_id"] = data["category"]
        if "staff" in data and "staff_id" not in data:
            data["staff_id"] = data["staff"]
        if "expired_at" in data and (data["expired_at"] == "" or data["expired_at"] == "null"):
            data["expired_at"] = None
        return super().to_internal_value(data)

    def validate(self, attrs):
        dtype_id = attrs.get("dtype_id")
        if dtype_id:
            try:
                dtype_obj = Dtype.objects.get(id=dtype_id)
                if not "temporary" in dtype_obj.dtype_name.lower():
                    attrs["expired_at"] = None
            except Dtype.DoesNotExist:
                pass
        return attrs
