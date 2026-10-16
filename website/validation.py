from PIL import Image

import re
from datetime import datetime

from flask import session


# Check that the uploaded profile picture is a valid image
def validate_profile_picture(file):
    try:
        # Open the uploaded file using Pillow
        image = Image.open(file)

        # Store the format before verify()
        image_format = image.format

        # DEBUGGING
        print("Original filename:", file.filename)
        print("Pillow detected format:", image_format)

        # Check dimensions
        width, height = image.size

        # Check actual image format
        if image_format not in ["PNG", "JPEG", "WEBP", "AVIF"]:
            return False, "Profile picture must be PNG, JPEG, WEBP or AVIF", None
        elif (width < 500 or height < 500) and (width > 4096 or height > 4096): # Make sure the image is not too small or too large
            return False, "Profile picture must be at least 500x500 pixels", None # Make sure the image is not too small or too large
        elif width != height:
            return False, "Profile picture must be square", None # Make sure the image is square
        else:
            # Check that the image is valid
            image.verify()

            # Reset file so it can be saved after
            file.seek(0)

            return True, None, image_format

    except Exception:
        return False, "Invalid image file", None



def all_validation_users(
        username,
        DOB,
        email,
        password,
        confirm_password
):

    # Check that none of the required fields are empty
    if (not username.strip()
            or not DOB.strip()
            or not email.strip()
            or not password.strip()
            or not confirm_password.strip()):

        error = "The form must be filled out"
        return False, error

    else:
        return True, None


# Check that the username is between 2 and 32 characters
def username_validation(username):
    username_re = r"^.{2,32}$"
    username_match = re.fullmatch(username_re, username)

    if not username_match:
        error = "Username must be between 2 and 32 characters"
        return False, error

    else:
        return True, None


# Compare the old value with the new value
def compare_old_and_new(code, user, value1, value2):

    # Check that the new username is not the same as the old username
    if code == "is_username":
        if value1 == session.get(value2):
            error = "New username cannot be the same as current username"
            return False, error
        else:
            return True, None

    # Check that the new value is not the same as the current value
    if code == "not_username":
        if value1 == user[value2]:
            error = f"New {value2} cannot be the same as current {value2}"
            return False, error
        else:
            return True, None


# Check that the date of birth is valid
def DOB_validation(DOB):
    try:
        dob = datetime.strptime(DOB, "%Y-%m-%d").date()

        # Make sure the date is not in the future
        if dob >= datetime.today().date():
            error = "The date must not be in the future"
            return False, error

    except ValueError:
        error = "You have provided an invalid date of birth"
        return False, error

    return True, None


# Check that the email follows the correct format
def email_validation(email):
    email_re = r"^[\w\.-]+@[a-zA-Z\-\.]+\.[a-zA-Z]{2,}$"
    email_match = re.match(email_re, email)

    if not email_match:
        error = "Invalid Email"
        return False, error

    else:
        return True, None


# Check that the password meets the required requirements
def password_validation(password):
    password_re = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9]).{8,}$"
    password_match = re.match(password_re, password)

    if not password_match:
        error = "Password must contain at least one digit, letter, capital letter and a special character"
        return False, error

    else:
        return True, None

def all_validation_albums(
        title,
        creator,
        creation_date,
        track_count,
):

    # Check that none of the required fields are empty
    if (not title.strip()
            or not creator.strip()
            or not creation_date.strip()
            or not track_count.strip()):

        error = "The form must be filled out"
        return False, error

    else:
        return True, None


# Check that the album title is between 1 and 100 characters
def title_validation(title):

    if len(title) < 1 or len(title) > 100:
        error = "Album title must be between 1 and 100 characters"
        return False, error

    else:
        return True, None


# Check that the creator name is between 1 and 100 characters
def creator_validation(creator):

    if len(creator) > 100 or len(creator) < 1:
        error = "Creator name must be between 1 and 100 characters"
        return False, error

    else:
        return True, None


# Check that the creation date is valid
def creation_date_validation(creation_date):
    try:
        formatted_date = datetime.strptime(
            creation_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        error = "You have provided an invalid creation date"
        return False, error

    # Make sure the creation date is not in the future
    if formatted_date > datetime.today().date():
        error = "Creation date cannot be in the future"
        return False, error

    return True, None


# Check that the track count is a number
def track_count_validation(track_count):

    if not track_count.isdigit():
        error = "Track count must be a number"
        return False, error

    return True, None


