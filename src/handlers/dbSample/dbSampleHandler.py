import os
import json
import logging
import casbin_sqlalchemy_adapter
import casbin

# Get environment variables
username = os.getenv("DB_USER")
password = os.environ.get("DB_PASSWORD")
host = os.environ.get("DB_HOST")
db_name = os.environ.get("DB_NAME")
# Set logger configurations
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Create connection to db
adapter = casbin_sqlalchemy_adapter.Adapter(
    f"postgresql://{username}:{password}@{host}/{db_name}"
)
casbin_sqlalchemy_adapter.CasbinRule
# Load Casbin configuration
e = casbin.Enforcer("./model.conf", adapter)


def handler(event, context):
    # Fake data to simulate request params
    sub = "b8b1294c-04b2-4245-9d4d-0ac60a7804b7"  # the user that wants to access a resource.
    obj = "3f70632a-2168-11ec-9621-0242ac130002"  # the resource that is going to be accessed.
    act = "read"  # the operation that the user performs on the resource.
    # Make a request to validate the permission
    validation = e.enforce(sub, obj, act)
    # validation2 = e.enforce(sub, obj, "write")
    # validation3 = e.enforce(sub, obj, "delete")
    # validation4 = e.enforce("bob", obj, "delete")
    # validation5 = e.enforce("bob", obj, "read")
    object = {"auth": validation, "sub": sub, "obj": obj, "act": "write"}
    # object2 = {
    #     'auth': validation2,
    #     'sub': sub,
    #     'obj': obj,
    #     'act': act
    # }
    # object3 = {
    #     'auth': validation3,
    #     'sub': sub,
    #     'obj': obj,
    #     'act': "delete"
    # }
    # object4 = {
    #     'auth': validation4,
    #     'sub': "bob",
    #     'obj': obj,
    #     'act': "delete"
    # }
    # object5 = {
    #     'auth': validation5,
    #     'sub': "bob",
    #     'obj': obj,
    #     'act': "read"
    # }

    # Add policy
    # e.add_policy(sub, obj, "read")
    # e.add_policy(sub, obj, "write")
    # e.add_policy("bob", obj, "read")

    # Remove specific policy
    # e.remove_policy([sub, obj, "read"])
    # e.remove_policy([sub, obj, "write"])
    # e.remove_policy(["bob", obj, "read"])

    # Get permissions for user
    # e.get_permissions_for_user(sub)
    # Get all permissions associated to obj or usr, or both

    # e.get_filtered_policy(0, "", obj)
    # Remove all policies associated to obj or usr
    e.remove_filtered_policy(0, "", obj)
    logger.info("Validation1" + str(json.dumps(object)))
    # logger.info("Validation2" + str(json.dumps(object2)))
    # logger.info("Validation3" + str(json.dumps(object3)))
    # logger.info("Validation4" + str(json.dumps(object4)))
    # logger.info("Validation5" + str(json.dumps(object5)))
    return {
        "statusCode": 202,
        "body": json.dumps(object),
        "headers": {"Content-Type": "application/json"},
    }
