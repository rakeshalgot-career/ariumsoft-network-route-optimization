from django.contrib import admin

from network.models import Edge, Node, RouteHistory


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "destination", "latency", "created_at")
    list_filter = ("source", "destination")
    search_fields = ("source__name", "destination__name")
    ordering = ("id",)


@admin.register(RouteHistory)
class RouteHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "destination", "total_latency", "created_at")
    list_filter = ("source", "destination", "created_at")
    search_fields = ("source__name", "destination__name")
    ordering = ("-created_at",)
