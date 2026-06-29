from rest_framework import serializers

from network.models import Edge, Node, RouteHistory


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required.")
        return value.strip()


class EdgeSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        slug_field="name", queryset=Node.objects.all()
    )
    destination = serializers.SlugRelatedField(
        slug_field="name", queryset=Node.objects.all()
    )

    class Meta:
        model = Edge
        fields = ["id", "source", "destination", "latency", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_latency(self, value):
        if value <= 0:
            raise serializers.ValidationError("Latency must be greater than 0.")
        return value

    def validate(self, attrs):
        if attrs["source"] == attrs["destination"]:
            raise serializers.ValidationError(
                "Source and destination must be different."
            )
        if Edge.objects.filter(
            source=attrs["source"], destination=attrs["destination"]
        ).exists():
            raise serializers.ValidationError("This edge already exists.")
        return attrs


class RouteRequestSerializer(serializers.Serializer):
    source = serializers.CharField()
    destination = serializers.CharField()

    def validate_source(self, value):
        if not Node.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                f"Node '{value}' does not exist."
            )
        return value

    def validate_destination(self, value):
        if not Node.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                f"Node '{value}' does not exist."
            )
        return value


class RouteHistorySerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )
    destination = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )

    class Meta:
        model = RouteHistory
        fields = [
            "id",
            "source",
            "destination",
            "total_latency",
            "path",
            "created_at",
        ]
