# Used for saving and deleting images to device
import os

# Used for creation the web application
from flask import current_app, flash
from flask import render_template, Blueprint, request, redirect, url_for, session

# Used for secure encryption
from werkzeug.security import generate_password_hash, check_password_hash

# Used for SQL logic that communicates with the backend
from db import gather_user_info, user_saved_albums, gather_saved_album_data
from db import gather_user_id, change_user_pfp, change_username
from db import change_email, change_pw_hash, gather_user_password, delete_user

# Used for validating user inputs
from validation import validate_profile_picture
from validation import username_validation, compare_old_and_new, email_validation, password_validation

catalogue = Blueprint('catalogues', __name__, template_folder='templates')

@catalogue.route('/', methods=['GET', 'POST'])
def account():
    if not session.get('username'):
        return redirect(url_for('views.login'))

    user = gather_user_info(session.get('username')) # Gather user data from current signed-in user

    saved_album_ids = user_saved_albums(session.get('username'))


    new_albums_first = saved_album_ids[::-1]
    selective_number_of_albums = new_albums_first[:50]
    formated_album_ids = selective_number_of_albums

    saved_albums = gather_saved_album_data(formated_album_ids)

    if request.method == 'POST':

        # Multiple forms on one page
        form_type = request.form['form_type']

        # Back end for changing user profile picture
        if form_type == 'profile-picture-change':

            # Validate the uploaded profile picture
            acProfile_picture = request.files['profile-picture']

            valid, error, image_format = validate_profile_picture(acProfile_picture)

            if not valid:
                flash("Validating your profile picture has failed. Please try again or try a different picture", "error")
                return redirect(url_for('catalogues.account'))

            # Convert JPEG to JPG for the filename
            if image_format == 'JPEG':
                extension = "jpg"
            else:
                extension = image_format.lower()

            # Gather the user id from the current logged-in user
            user_id = gather_user_id(session.get('username'))

            # Create the filename using the user ID
            filename = f"{user_id}_pfp.{extension}"

            # Create the location where the image will be saved
            savepath = os.path.join(
                current_app.root_path,
                "static",
                "profile_pictures",
                filename
            )

            # Remove the user's old profile picture
            for old_extension in ["png", "jpg", "jpeg", "webp", "avif"]: # Cycles through each possible format

                old_path = os.path.join(
                    current_app.root_path,
                    "static",
                    "profile_pictures",
                    f"{user_id}_pfp.{old_extension}"
                )

                if os.path.exists(old_path):
                    os.remove(old_path) # Delete old profile picture

            # Save the new profile picture
            acProfile_picture.save(savepath)

            # Create the path that will be stored in the database
            pfp_path = f"/static/profile_pictures/{filename}"

            try:
                # Saves the filepath of the uploaded pfp in the database
                change_user_pfp(
                    pfp_path,
                    session.get('username')
                )

                flash("Your profile picture has successfully been changed", "success")
                return redirect(url_for('catalogues.account'))

            except Exception as e:
                flash("Changing your profile picture has failed. Please try again or try a different picture", "error")
                return redirect(url_for('catalogues.account'))

        # Back end for changing user username
        if form_type == 'username-change':
            newUsername = request.form['username']

            #------------
            # Validation
            #------------

            if (not newUsername.strip()):
                flash("The form must be filled out", "information")
                return redirect(url_for('catalogues.account'))

            code = "is_username"
            value2 = "username"

            validations = [
                    (username_validation, (newUsername)),
                    (compare_old_and_new, (code, None, newUsername, value2)),
            ]

            for validation, values in validations:
                if validation == compare_old_and_new:
                    status, error = validation(*values)
                    flash(error, "information")

                else:
                    status, error = validation(values)
                    flash(error, "information")

                if status is False:
                    flash(error, "information")
                    return redirect(url_for('catalogues.account'))
            else:
                try:
                    # Gather the user id from the current logged-in user
                    user_id = gather_user_id(session.get('username'))

                    # Replace the old username with the new username
                    change_username(newUsername, user_id)

                    flash("Your username has successfully been changed", "success")
                    # Pops current session by changing username and going to the login page

                    session['username'] = newUsername

                    return redirect(url_for('catalogues.account'))
                except Exception:
                    flash("This username is being used by someone else. Please try a different one", "information")
                    return redirect(url_for('catalogues.account'))

        # Back end for changing user email
        if form_type == 'email-change':
            newEmail = request.form['email']

            # Gather current users data
            user = gather_user_info(session.get('username'))

            #------------
            # Validation
            #------------

            if (not newEmail.strip()):
                flash("The form must be filled out", "information")
                return redirect(url_for('catalogues.account'))

            code = "not_username"
            value2 = "email"

            validations = [
                    (email_validation, (newEmail)),
                    (compare_old_and_new, (code, user, newEmail, value2)),
            ]

            for validation, values in validations:
                if validation == compare_old_and_new:
                    status, error = validation(*values)
                    flash(error, "information")

                else:
                    status, error = validation(values)
                    flash(error, "information")

                if status is False:
                    flash(error, "information")
                    return redirect(url_for('catalogues.account'))
            else:
                try:
                    # Gather the user id from the current logged-in user
                    user_id = gather_user_id(session.get('username'))

                    # Replace the old email with the new email
                    change_email(newEmail, user_id)

                    flash("Your email has successfully been changed", "success")
                    return redirect(url_for('catalogues.account')) # Logs user out and takes them to the login page
                except Exception as e:
                    flash("This email is being used by someone else. Please try a different one", "information")
                    return redirect(url_for('catalogues.account'))

        # Back end for changing user password
        if form_type == 'password-change':
            newPassword = request.form['new_password']

            #------------
            # Validation
            #------------


            if (not newPassword.strip()):
                flash("The form must be filled out", "information")
                return redirect(url_for('catalogues.account'))

            status, error = password_validation(newPassword)
            if status is False:
                flash(error, "information")
                return redirect(url_for('catalogues.account'))
            else:
                try:
                    # Gather the user id from the current logged-in user
                    user_id = gather_user_id(session.get('username'))

                    # Gather the users hashed password
                    old_password_hash = gather_user_password(user_id)

                    # Check if the old password hashed matches the new one hashed
                    if check_password_hash(old_password_hash, newPassword):
                        flash("New password cannot be the same as current password", "success")
                        return redirect(url_for('catalogues.account'))

                    # Hash the new password
                    newPw_hash = generate_password_hash(newPassword)

                    # Replace the old password hashed with the new hashed password
                    change_pw_hash(newPw_hash, user_id)

                    flash("Your password has successfully been changed", "success")
                    return redirect(url_for('catalogues.account')) # Logs user out and takes them to the login page
                except Exception as e:
                    flash("Changing your password has failed. Please try again later",
                          "error")
                    return redirect(url_for('catalogues.account'))

        if form_type == 'account-deletion':
            confirmation = request.form['account-deletion'] # If the user submits the form to delete there account

            try:
                if confirmation == "DELETE": # The user has to enter "DELETE" to be exact
                    user_id = gather_user_id(session.get('username')) # Gather the id of the current signed in user

                    delete_user(user_id, session.get('username')) # Delete the user by there id and there username

                    flash("Your account has successfully been deleted", "success")
                    return redirect(url_for('views.logout'))
                else:
                    flash("Please enter exactly 'DELETE' in order to delete your account", "success")
                    return redirect(url_for('catalogues.account'))
            except:
                flash("Please enter exactly 'DELETE' in order to delete your account", "success")
                return redirect(url_for('catalogues.account'))

        if form_type == 'album-input':

    return render_template("account.html", user=user, saved_albums=saved_albums)
