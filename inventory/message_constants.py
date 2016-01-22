"""All messages and emails in the system are written here"""

ALREADY_LOGGED_MESSAGE = 'You are already logged in'
LOGIN_REQUIRED_MESSAGE = 'You need to login First'
LOGIN_SUCCESS_MESSAGE = 'You have been logged in'
LOGIN_INVALID_MESSAGE = 'Please check your credentials'
LOGOUT_SUCCESS_MESSAGE = 'You have been logged out'
REQUEST_SUBMITTED_MESSAGE = 'Your request has been submitted'


def item_added_message(item_name):
    """Generate confirmation message for new item added into inventory"""
    return item_name + ' has been added to inventory'


def item_added_mail(item_name, item_quantity):
    """Generate email for new item added into inventory"""
    new_mail = {
        'subject': 'New Inventory Item Added',
        'body': item_name + ' has been added to inventory. Quantity added is ' + str(item_quantity)
    }

    return new_mail


def item_edited_message(item_name):
    """Generate confirmation message for an item updated"""
    return item_name + ' has been updated successfully'


def item_edited_mail(item_name):
    """Generate email for an item updated"""
    new_mail = {
        'subject': 'Inventory Item Updated',
        'body': 'Inventory Item - ' + item_name + ' has been updated.'
    }

    return new_mail


def item_returned_mail(user_email):
    """Generate email for an item marked as returned"""
    new_mail = {
        'subject': 'Inventory Item Marked Returned',
        'body': 'An inventory item has been returned by ' + user_email
    }

    return new_mail


def item_provision_message(item_name, user_email):
    """Generate confirmation message for an item provisioned"""
    return item_name + ' is provisioned to ' + user_email


def item_provision_mail(item_name, user_email):
    """Generate email when an item is provisioned"""
    new_mail = {
        'subject': 'Inventory Item Provisioned',
        'body': 'An inventory item has been provisioned to a user. User - ' + user_email + ', item - ' + item_name
    }

    return new_mail
