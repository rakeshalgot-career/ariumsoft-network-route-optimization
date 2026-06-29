from django.urls import path

from network import views

urlpatterns = [
    path("nodes/", views.node_list_create, name="node-list-create"),
    path("nodes/<int:pk>/", views.node_delete, name="node-delete"),
    path("edges/", views.edge_list_create, name="edge-list-create"),
    path("edges/<int:pk>/", views.edge_delete, name="edge-delete"),
    path("routes/shortest/", views.shortest_route, name="shortest-route"),
    path("routes/history/", views.route_history, name="route-history"),
]
