from datetime import datetime
import logging
from http import HTTPStatus

from django.contrib.auth.models import User
from django.db.models import F, Min, Sum
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import *
from core.serializers import *

# Create your views here.

logger = logging.getLogger(__name__)


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class ProductDetailViewSet(viewsets.ModelViewSet):
    queryset = ProductDetail.objects.all()
    serializer_class = ProductDetailSerializer

    @action(detail=False, methods=["get"], url_path="product/(?P<my_pk>[^/.]+)")
    def get_product_details(self, request, my_pk=None):
        # if product id is not provided
        if my_pk is None:
            return Response(
                data="Please provide product id.",
                status=HTTPStatus.HTTP_400_BAD_REQUEST,
            )

        # aggregate with stores to find where it is available along with lowest price
        queryset = (
            Product.objects.filter(product_id=my_pk, quantity__gt=0.0)
            .values(
                _id=F("product_id"),
                store_id=F("retail_store_id"),
                store_name=F("retail_store__name"),
                brand_name=F("product__brand__name"),
                brand_id=F("product__brand_id"),
                seller_id=F("retailer_id"),
            )
            .annotate(quant=Sum("quantity"), min_price=Min("price"))
        )
        orders = list(queryset)

        # fetching valid promotions on product
        now = datetime.now()
        promotions = Promotion.objects.filter(
            start_date__lte=now, end_date__gte=now
        )

        for order in orders:
            # placeholder for list of applicable promotions
            order["promotions"] = list()

            for promotion in promotions:
                # filtering on brand
                if (
                    promotion.brand is not None
                    and promotion.brand_id != order.get("brand_id")
                ):
                    continue
                # filtering on product
                if (
                    promotion.product is not None
                    and promotion.product_id != order.get("_id")
                ):
                    continue
                # filtering on store
                if (
                    promotion.retail_store is not None
                    and promotion.retail_store_id != order.get("store_id")
                ):
                    continue
                # filtering on retailer
                if (
                    promotion.retailer is not None
                    and promotion.retailer_id != order.get("seller_id")
                ):
                    continue

                # promotion is valid on the order
                promotion_data = dict()
                promotion_data["id"] = promotion.id
                promotion_data["name"] = promotion.name
                # calculating discount using promotion
                if promotion.promotion_type == "PERCENTAGE":
                    discount = (promotion.value * order.get("min_price")) / 100
                else:
                    discount = promotion.value
                promotion_data["discount"] = discount
                promotion_data["discounted_price"] = (
                    order.get("min_price") - discount
                )
                order["promotions"].append(promotion_data)

        # providing list of stores where this product is not available
        available_stores = list(
            queryset.values_list("store_id", flat=True).distinct()
        )
        not_available_stores = list(
            RetailStore.objects.exclude(id__in=available_stores).values_list(
                "id", flat=True
            )
        )
        #appending store availability data to orders
        orders.insert(
            0,
            {
                "available_stores": available_stores,
                "not_available": not_available_stores,
            },
        )

        return Response(orders)


class RetailStoreViewSet(viewsets.ModelViewSet):
    queryset = RetailStore.objects.all()
    serializer_class = RetailStoreSerializer


class RetailerViewSet(viewsets.ModelViewSet):
    queryset = Retailer.objects.all()
    serializer_class = RetailerSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ["get", "post", "put", "patch"]

    def update(self, request, pk, *args, **kwargs):
        # check for price change
        # to-do: this can be shifted
        update_data = request.data
        try:
            product = Product.objects.get(id=pk)
        except User.DoesNotExist:
            logger.warning(f"[UPDATE-PRODUCT] - Invalid product id: {pk}")
            return Response(
                {"detail": "Invalid product id"}, HTTPStatus.BAD_REQUEST
            )
        try:
            update_price = float(update_data.get("price"))
            if product.price != update_price:
                # price increase
                if update_price > product.price:
                    logger.info(f"[ISSUE-ALERT] - Price has been increased from {product.price} to {update_price}")
                    # Issuing a alert
                    alert = Alert.objects.create(
                        created_at=datetime.now(),
                        alert_type="PRICE_INCREASE",
                        product_id=pk,
                        desc="Price has been increased from {} to {}".format(
                            product.price, update_price
                        ),
                    )
                else:
                    logger.info(f"[ISSUE-ALERT] - Price has been decreased from {product.price} to {update_price}")
                    # Issuing a alert
                    alert = Alert.objects.create(
                        created_at=datetime.now(),
                        alert_type="PRICE_DECREASE",
                        product_id=pk,
                        desc="Price has been decreased from {} to {}".format(
                            product.price, update_price
                        ),
                    )

            # to update product
            product.price = update_price
            product.quantity = update_data.get("quantity")
            product.retailer_id = update_data.get("retailer")
            product.retail_store_id = update_data.get("retail_store")
            product.product_id = update_data.get("product")
            product.save(
                update_fields=[
                    "price",
                    "quantity",
                    "retailer_id",
                    "retail_store_id",
                    "product_id",
                ]
            )
            # serializer = self.get_serializer(data=update_data)
            return Response(update_data, status=HTTPStatus.OK)
        except Exception as e:
            return Response(
                {"detail": "Exception updating product"}, HTTPStatus.BAD_REQUEST
            )

    @action(detail=False, methods=["get"], url_path="all")
    def get_products(self, request):
        queryset = (
            Product.objects.values(
                _id=F("product_id"),
                name=F("product__name"),
                brand=F("product__brand__name"),
            )
            .annotate(quantity=Sum("quantity"), price=Min("price"))
            .order_by()
        )

        return Response(queryset)


class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    http_method_names = ["get", "post"]

    # prohibiting promotion creation
    def create(self, request):
        logger.warning(f"[Promotion] - Invalid endpoint | valid endpoint is /promotion/create")
        return Response(
            data={"detail": "Valid endpoint is /promotion/create"},
            status=HTTPStatus.NOT_FOUND,
        )

    @action(detail=False, methods=["POST"], url_path="create")
    def run_promotion(self, request, *args, **kwargs):
        # checking token is present
        key = request.headers.get("Authorization", None)
        if not key:
            logger.warning(f"[Promotion] - Missing Authorization Token")
            return Response(
                {"detail": "Missing Authorization Token"},
                HTTPStatus.BAD_REQUEST,
            )
        try:
            token = Token.objects.get(key=key)
        except:
            logger.warning(f"[Promotion] - Invalid Authorization Token")
            return Response(
                {"detail": "Invalid Authorization Token"},
                HTTPStatus.BAD_REQUEST,
            )

        super().create(request, *args, **kwargs)
        return Response(data=request.data, status=HTTPStatus.OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ["get", "post", "put", "patch"]

    # user login API
    @action(detail=False, methods=["POST"], url_path="login")
    def login(self, request):
        login_request = request.data
        try:
            user = User.objects.get(username=login_request.get("username"))
            authenticated = user.check_password(login_request.get("password"))
            # work-around since manually created user doesn't have encrypted password stored
            # to-do: store password after encrypting it.
            if not authenticated:
                if user.password == login_request.get("password"):
                    authenticated = True
                else:
                    authenticated = False
        except User.DoesNotExist as e:
            logger.warning(f"[LOGIN] - Invalid username")
            return Response(
                data={"status": "Failure", "detail": "Invalid username"},
                status=HTTPStatus.BAD_REQUEST,
            )
        if authenticated:
            token, created = Token.objects.get_or_create(user_id=user.id)
            return Response(
                data={"status": "Success", "token": token.key},
                status=HTTPStatus.OK,
            )
        else:
            logger.warning(f"[LOGIN] - Invalid password")
            return Response(
                data={"status": "Failure", "detail": "Invalid password"},
                status=HTTPStatus.BAD_REQUEST,
            )

    # user sign-up API
    @action(detail=False, methods=["POST"], url_path="register")
    def register(self, request):
        signup_request = request.data
        try:
            user = User.objects.create(**signup_request)
        except Exception as e:
            logger.warning(f"[LOGIN] - Duplicate username")
            return Response(
                data={"status": "Failure", "detail": "Duplicate username"},
                status=HTTPStatus.BAD_REQUEST,
            )

        return Response(signup_request, status=HTTPStatus.OK)


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    http_method_names = ["get"]
