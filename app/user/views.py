from . import user
from app.models import *
from flask import render_template, redirect
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, TextField
from wtforms.validators import Regexp, Optional


@user.route('/user/<username>/<int:page_num>', methods=['GET', 'POST'])
def show_user(username, page_num):
    user = User.query.filter_by(username=username).first()
    announcements = Announcement.query.filter_by(creator=username).order_by(Announcement.date.desc()).paginate(
        per_page=5, page=page_num, error_out=True)
    return render_template('user.html', user=user, announcements=announcements)


@user.route('/user/editbio', methods=['GET', 'POST'])
@login_required
def edit_bio():
    class EditBioForm(FlaskForm):
        if current_user:
            bio = TextAreaField('Twój opis', default=current_user.bio)
            submit = SubmitField('Zapisz')

    form = EditBioForm()
    if form.validate_on_submit():
        current_user.bio = form.bio.data
        db.session.commit()
    return render_template('editbio.html', form=form)


@user.route('/user/add_links', methods=['GET', 'POST'])
@login_required
def add_links():
    class LinkForm(FlaskForm):
        if current_user:
            steam = TextField('Link do Twojego konta steam:', default=current_user.steamID,
                            validators=[Regexp('https://steamcommunity.com/profiles/[0-9]*',
                            message='Niepoprawny link, skopiuj cały link ze strony'), Optional()])
            lol = TextField('Link do Twojego konta na op.gg', default=current_user.lolProfileLink,
                            validators=[Regexp('https://[a-z]{2,4}\.op\.gg/summoner/userName=.*',
                            message='Niepoprawny link, skopiuj cały link ze strony'), Optional()])
            discord = TextField('Twój Discord:', default=current_user.discord, validators=[Regexp('.*#[0-9]{4}',
                            message='Niepoprawny nick discordowy'), Optional()])
            submit = SubmitField('Zatwierdź zmiany')

    form = LinkForm()
    if form.validate_on_submit():
        current_user.lolProfileLink = form.lol.data
        current_user.steamID = form.steam.data
        current_user.discord = form.discord.data
        db.session.commit()
        return redirect(f'/user/{current_user.username}/1')
    return render_template('profiles.html', form=form)
