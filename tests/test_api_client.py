"""ApiClientGenerator : 100% déterministe, testable sans LLM."""
from services.frontend.agents.api_client_node import ApiClientGenerator, _camel

SPEC = {
    "openapi": "3.0.0",
    "components": {
        "schemas": {
            "Product": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                },
            },
            "ProductCreate": {
                "type": "object",
                "required": ["name", "price"],
                "properties": {
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                },
            },
        }
    },
    "paths": {
        "/products": {
            "post": {
                "operationId": "create_product",
                "requestBody": {"content": {"application/json": {
                    "schema": {"$ref": "#/components/schemas/ProductCreate"}}}},
                "responses": {"201": {"content": {"application/json": {
                    "schema": {"$ref": "#/components/schemas/Product"}}}}},
            },
            "get": {
                "operationId": "list_products",
                "responses": {"200": {"content": {"application/json": {
                    "schema": {"type": "array",
                               "items": {"$ref": "#/components/schemas/Product"}}}}}},
            },
        },
        "/products/{id}": {
            "get": {
                "operationId": "get_product_by_id",
                "parameters": [{"name": "id", "in": "path", "required": True,
                                "schema": {"type": "integer"}}],
                "responses": {"200": {"content": {"application/json": {
                    "schema": {"$ref": "#/components/schemas/Product"}}}}},
            },
            "delete": {
                "operationId": "delete_product",
                "parameters": [{"name": "id", "in": "path", "required": True,
                                "schema": {"type": "integer"}}],
                "responses": {"204": {}},
            },
        },
    },
}


def test_camel_case():
    assert _camel("create_product") == "createProduct"
    assert _camel("get_product_by_id") == "getProductById"


def test_generates_interfaces():
    code = ApiClientGenerator(SPEC).generate()
    assert "export interface Product {" in code
    assert "export interface ProductCreate {" in code


def test_generates_all_functions():
    code = ApiClientGenerator(SPEC).generate()
    for fn in ["createProduct", "listProducts", "getProductById", "deleteProduct"]:
        assert f"export async function {fn}(" in code


def test_path_param_is_typed():
    code = ApiClientGenerator(SPEC).generate()
    assert "getProductById(id: number)" in code





def test_is_deterministic():
    a = ApiClientGenerator(SPEC).generate()
    b = ApiClientGenerator(SPEC).generate()
    assert a == b