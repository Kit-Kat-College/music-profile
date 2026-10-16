# Used for saving and deleting images to device
import os

# Used for creation the web application
from flask import current_app, flash
from flask import render_template, Blueprint, request, redirect, url_for, session

# Used for secure encryption
from werkzeug.security import generate_password_hash, check_password_hash

# Used for SQL logic that communicates with the backend
from db import gather_user_info, insert_user, check_if_album_is_registered, insert_album, update_saved_records
from db import check_if_album_is_saved, change_album_cover, gather_user_id, change_user_pfp, change_username

# Used for validating user inputs
from validation import validate_profile_picture
from validation import all_validation_users, username_validation, compare_old_and_new, DOB_validation, email_validation, password_validation
from validation import all_validation_albums, title_validation, creator_validation, creation_date_validation, track_count_validation

view = Blueprint('views', __name__, template_folder='templates')


@view.route('/album_input', methods=['GET', 'POST'])
def album_input():

    # Stop users from accessing the page if they are not logged in
    if not session.get('username'):
        return redirect(url_for('views.login'))

    if request.method == 'POST':
        aiTitle = request.form['title']
        aiCreator = request.form['creator']
        aiCreation_date = request.form['creation_date']
        aiTrack_count = request.form['track_count']
        aiCover = request.files['cover']

        # -----------
        # Validation
        # ------------

        validations = [
            (all_validation_albums, (aiTitle, aiCreator, aiCreation_date, aiTrack_count)),
            (title_validation, aiTitle),
            (creator_validation, aiCreator),
            (creation_date_validation, aiCreation_date),
            (track_count_validation, aiTrack_count)
        ]

        for validation, value in validations:
            try:
                if validation == all_validation_albums:  # The only function that requires multiple variables
                        status, error = validation(*value)  # * accepts multiple values
                else:
                    status, error = validation(value)

            except ValueError:  # Less than 5 or more than 5 values
                flash("We had trouble processing this request, please try again later", "error")
                return redirect(url_for('views.album_input'))

            if not status:
                flash(error, "information")
                return redirect(url_for('views.album_input'))


        # ------------------------------------------------
        # VALIDATE ALBUM COVER BEFORE CREATING ALBUM
        # ------------------------------------------------

        image_format = None

        if aiCover and aiCover.filename:

            try:
                # Validate the uploaded cover
                valid, error, image_format = validate_profile_picture(
                    aiCover
                )

                if not valid:
                    print(error, "information")
                    return redirect(url_for('views.album_input'))

            except Exception as e:
                flash("Album cover validation has failed, please try again later or try a different picture", "error")
                return redirect(url_for('views.album_input'))

        # ------------------------------------------------
        # CHECK WHETHER ALBUM ALREADY EXISTS
        # ------------------------------------------------

        prior_album_id = check_if_album_is_registered(
            aiTitle,
            aiCreator
        )

        # ------------------------------------------------
        # ALBUM ALREADY EXISTS
        # ------------------------------------------------

        if prior_album_id is not None:

            # Save the existing album to the user's profile
            update_saved_records(
                session.get('username'),
                prior_album_id
            )

            flash(
                "The album is already registered and has been saved to your account",
                "success"
            )

            return redirect(url_for('views.album_input'))

        # ------------------------------------------------
        # ALBUM DOES NOT EXIST
        # ------------------------------------------------

        else:

            # Uses the default cover initially
            # This is replaced later if the user uploaded a cover
            cover_path = "/static/album_covers/default_song_cover.png"

            # Gather the user id from the current logged-in user
            user_id = gather_user_id(
                session.get('username')
            )

            # ------------------------------------------------
            # INSERT ALBUM INTO DATABASE
            # ------------------------------------------------

            insert_album(
                aiTitle,
                aiCreator,
                aiCreation_date,
                cover_path,
                aiTrack_count,
                user_id
            )

            # Get the ID of the album we just inserted
            new_album_id = check_if_album_is_registered(
                aiTitle,
                aiCreator
            )

            # ------------------------------------------------
            # SAVE UPLOADED ALBUM COVER
            # ------------------------------------------------

            if aiCover and aiCover.filename:

                # Convert JPEG to JPG for the filename
                if image_format == "JPEG":
                    extension = "jpg"
                else:
                    extension = image_format.lower()

                # Create the filename using the album ID
                filename = f"{new_album_id}_cover.{extension}"

                # Create the location where the image will be saved
                save_path = os.path.join(
                    current_app.root_path,
                    "static",
                    "album_covers",
                    filename
                )

                try:

                    # Save the uploaded image to the PC
                    aiCover.save(save_path)

                    # Create the path that will be stored in the database
                    cover_path = f"/static/album_covers/{filename}"

                    # Change the album's cover from the default
                    # to the uploaded cover
                    change_album_cover(
                        cover_path,
                        new_album_id
                    )

                except Exception as e:

                    flash(
                        "Saving this album cover has failed. Please try again later in account settings",
                        "error"
                    )

                    return redirect(
                        url_for('views.album_input')
                    )

            # ------------------------------------------------
            # SAVE ALBUM TO USER
            # ------------------------------------------------

            try:

                if not check_if_album_is_saved(
                    session.get('username'),
                    new_album_id
                ):

                    update_saved_records(
                        session.get('username'),
                        new_album_id
                    )

                    flash(
                        "The album has been registered and has been saved to your account",
                        "success"
                    )

                else:

                    flash(
                        "The album has been registered and is already saved to your account"
                        "information"
                    )

            except Exception as e:

                flash(
                    "Saving this album has failed. Please try again later",
                    "error"
                )

            return redirect(
                url_for('views.album_input')
            )

    return render_template("album_input.html")

@view.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # If user submits a form
        # Gather entered details
        logUsername = request.form['username']
        logPassword = request.form['password']

        # -----------
        # Validation
        # ------------

        if (not logUsername.strip()
                or not logPassword.strip()):
            flash("The form must be filled out", "information")
            return redirect(url_for('views.login'))

        # ---------
        # Database
        # ----------

        # Find the user matching the supplied username | SQL in db.py
        user_data = gather_user_info(logUsername)

        # Check if account exists
        if user_data is None:
            flash("This user is not saved in our system. Please try again", "information")
            return redirect(url_for("views.login"))
        else:
            # Check password
            if check_password_hash(user_data['hashed_pw'], logPassword):

                # Keeps user signed in on their device even after closing the website
                session['username'] = logUsername

                flash(f"Welcome back {logUsername}", "success")
                return redirect(url_for("catalogues.account"))
            else:
                flash("This user is not saved in our system. Please register your account", "information")
                return redirect(url_for("views.login"))

    return render_template("login.html")

@view.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST': # If user submits a form
        # Gather entered details
        signUsername = request.form['username']
        signDOB = request.form['DOB']
        print("DOB:", repr(signDOB))

        signEmail = request.form['email']
        signPassword = request.form['password']
        signConfirmPassword = request.form['confirm_password']

        pw_hashed = generate_password_hash(signPassword)

        # File path for default pfp | Every new user gets assigned said pfp
        default_profile_pfp = "/static/profile_pictures/default_pfp.png"

        #-----------
        # Validation
        #------------

        validations = [
            (all_validation_users, (signUsername, signDOB, signEmail, signPassword, signConfirmPassword)),
            (username_validation, signUsername),
            (DOB_validation, signDOB),
            (email_validation, signEmail),
            (password_validation, signPassword)
        ]

        for validation, value in validations:
            try:
                if validation == all_validation_users: # The only function that requires multiple variables
                    status, error = validation(*value) # * accepts multiple values
                else:
                    status, error = validation(value)

            except ValueError as e: # Less than 5 or more than 5 values
                flash("Validating your details has failed. Please try again later", "error")
                return redirect(url_for('views.register'))

            if not status:
                flash(error, "information")
                return redirect(url_for('views.register'))

        #---------
        # Database
        #----------

        try:
            # Insert new user into the database | SQL in db.py
            insert_user(signUsername, signDOB, signEmail, pw_hashed, default_profile_pfp)

            flash("Your account has successfully been registered", "success")

            # Keeps user signed in on their device even after closing the website
            session['username'] = signUsername

            return redirect(url_for('catalogues.account'))

        except: # The account is already in the database | Raises UNIQUE error
            flash("This user is saved in our system. Please login with a different account", "information")
            return redirect(url_for('views.register'))

    return render_template("register.html")

@view.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('views.login'))