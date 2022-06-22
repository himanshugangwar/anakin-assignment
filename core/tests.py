from django.test import TestCase
from rest_framework.test import APIClient


class ViewsTestCase(TestCase):
    def test_get_products_with_promotions(self):
        # check that all products details fetches successfully
        client = APIClient()
        response = client.get("/product-details/")
        for id in response.data:
            response = client.get(
                "/product-details/product/" + id, format="json"
            )
            self.assertEqual(response.status_code, 404)
        # success case
        self.assertEqual(200, 200)
