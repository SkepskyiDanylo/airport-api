from rest_framework import serializers
from airport.models import AirplaneType, Airplane


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
        )


class AirplaneListSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(
        source="type.name",
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "tail_number",
            "manufacturer",
            "type_name",
            "model",
            "status",
            "last_inspection",
            "rows",
            "seats_in_row",
            "total_seats",
            "image",
        )


class AirplaneEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = (
            "id",
            "tail_number",
            "manufacturer",
            "type",
            "model",
            "status",
            "last_inspection",
            "rows",
            "seats_in_row",
            "total_seats",
        )

class AirplaneImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = (
            "id",
            "image",
        )