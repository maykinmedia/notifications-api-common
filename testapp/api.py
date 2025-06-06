from rest_framework import routers, serializers, viewsets

from notifications_api_common.kanalen import Kanaal
from notifications_api_common.viewsets import NotificationViewSetMixin

from .models import Person


# serializers
class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ("url", "name", "address_street", "address_number")


# viewsets
class PersonViewSet(NotificationViewSetMixin, viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    notifications_kanaal = Kanaal(
        "personen",
        main_resource=Person(),
        kenmerken=("name", "address_street"),
        extra_kwargs={"address_street": {"help_text": "custom help text"}},
    )

    def get_notification_main_object_url(self, data: dict, kanaal: Kanaal):
        return data["url"]


# URL routing
router = routers.DefaultRouter()
router.register("persons", PersonViewSet)
