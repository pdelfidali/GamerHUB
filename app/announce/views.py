from datetime import datetime, timezone
from flask import Blueprint, redirect, render_template, flash, make_response, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, TextAreaField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, Required
from . import announce
from flask_login import login_required, current_user
from ..models import Announcement, User, Comment, Game
from main import db
from sqlalchemy import desc

all = 'Wszystkie gry'


@announce.route('/announce', methods=['GET', 'POST'])
@login_required
def add_announcement():
    class AnnounceForm(FlaskForm):
        title = StringField('Wprowadź nazwę ogłoszenia:', validators=[DataRequired(message='Wprowadź tytuł'),
                                                                      Length(min=5, max=30, message='Tytuł musi mieć pomiędzy 5 a 30 znaków')])
        data = TextAreaField('Wprowadź treść ogłoszenia:', validators=[DataRequired(message='Treść nie może być pusta'),
                                                                     Length(max=1500, message='Treść nie może być dłuższa niż 1500 znaków')])
        players = IntegerField('Ilu współgraczy potrzebujesz:', default=1, validators=[Required('Wprowadź liczbę')])
        games_list = []
        try:
            for game in Game.query.with_entities(Game.name):
                games_list.append(game[0])
        except:
            pass
        game = SelectField('Wybierz grę do której szukasz partnerów:', choices=games_list, validators=[Required('Dodaj grę')])
        submit = SubmitField('Zatwierdź')

    class AddGameForm(FlaskForm):
        name = StringField('Nazwa gry', validators=[DataRequired(message='Wprowadż tytuł'),
                                                    Length(min=2, max=64, message='Tytuł musi mieć pomiędzy 2 a 64 znaków')])
        submit = SubmitField('Dodaj grę')

    form = AnnounceForm()
    add_game_form = AddGameForm()
    if add_game_form.validate_on_submit():
        if Game.query.filter_by(name=add_game_form.name.data).first():
            flash('Gra jest już w bazie danych')
        else:
            game = Game(name=add_game_form.name.data)
            db.session.add(game)
            db.session.commit()
        return redirect('/announce')
    elif form.validate_on_submit():
        announcement = Announcement(title=form.title.data, content=form.data.data, date=datetime.now(timezone.utc),
                                    creator=current_user.username, game=form.game.data, amount=form.players.data,
                                    lastEdit=datetime.now(timezone.utc))
        db.session.add(announcement)
        db.session.commit()
        flash('Poprawnie dodano ogłoszenie')
        return redirect('/announce')
    return render_template('add_announcement.html', form=form, add_game_form=add_game_form)


@announce.route('/announcement/<int:page_num>', methods=['GET', 'POST'])
def display_announcements(page_num):
    class FiltersForm(FlaskForm):
        games_list = [all]
        try:
            for game in Game.query.with_entities(Game.name):
                games_list.append(game[0])
            # swap
            games_list.insert(0, games_list.pop(games_list.index(request.cookies.get('game'))))
        except:
            pass

        game = SelectField('Gra:', choices=games_list)
        if request.cookies.get('amount') and request.cookies.get('amount') != 'None':
            amount = IntegerField('Ilość osób', validators=[Optional()], default=request.cookies.get('amount'))
        else:
            amount = IntegerField('Ilość osób', validators=[Optional()])
        sort = RadioField('Sortuj po', choices=[('add', 'czasie dodania'), ('edit', 'czasie edycji')],
                          default=request.cookies.get('sort'))
        submit = SubmitField('Zastosuj filtry')
        clear = SubmitField('Wyczyść filtr')
    form = FiltersForm()
    # Z ciastkaiem:
    announcements = get_announcements(page_num, request.cookies.get('game'), request.cookies.get('amount'), request.cookies.get('sort'))

    # Zmiana ciastka
    if form.validate_on_submit():
        res = make_response(redirect('/announcement/1'))
        if form.submit.data:
            res.set_cookie('game', form.game.data)
            res.set_cookie('amount', str(form.amount.data))
            res.set_cookie('sort', form.sort.data)
        elif form.clear.data:
            res.set_cookie('game', all)
            res.set_cookie('amount', 'None')
            res.set_cookie('sort', 'add')
        return res

    return render_template('display_announcements.html', announcements=announcements, form=form)


@announce.route('/view_announcement/<int:ann_id>', methods=['GET', 'POST'])
def view_announcement(ann_id):
    class CommentForm(FlaskForm):
        comment = TextAreaField('Treść', validators=[DataRequired(message='Komentarz musi zawierać treść')])
        submit = SubmitField('Dodaj komentarz')

    announcement = Announcement.query.filter_by(id=ann_id).first()

    class EditForm(FlaskForm):
        announcement = Announcement.query.filter_by(id=ann_id).first()
        new_amount = IntegerField('Ilość osób:', default=announcement.amount)
        close = BooleanField('Ogłoszenie otwarte', default=announcement.open)
        submit = SubmitField('Zatwierdź zmiany')

    comment_form = CommentForm()
    edit_form = EditForm()
    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(creator=current_user.username,
                              content=comment_form.comment.data,
                              date=datetime.now(timezone.utc), announcement=ann_id)
            db.session.add(comment)
            db.session.commit()
            return redirect(f'/view_announcement/{ann_id}')
        else:
            flash('Musisz być zalogowany, żeby dodać komentarz')
    if edit_form.validate_on_submit():
        print(edit_form.close.data)
        announcement.amount = edit_form.new_amount.data
        announcement.open = edit_form.close.data
        announcement.lastEdit = datetime.now(timezone.utc)
        db.session.commit()
        return redirect(f'/view_announcement/{ann_id}')
    comments = Comment.query.filter_by(announcement=ann_id)
    return render_template('view_announcement.html', announcement=announcement, comment_form=comment_form,
                           edit_form=edit_form, comments=comments)


def get_announcements(page_num, game=None, amount=None, sort='add'):
    if sort == 'add':
        order = Announcement.date.desc()
    else:
        order = Announcement.lastEdit.desc()
    if (game and game != all) and amount and amount != 'None':
        amount = int(amount)
        return Announcement.query.filter(Announcement.game == game, Announcement.amount >= amount,
                                         Announcement.open).order_by(
            order). \
            paginate(per_page=5, page=page_num, error_out=True)
    if game and game != all:
        return Announcement.query.filter_by(game=game, open=True).order_by(order). \
            paginate(per_page=5, page=page_num, error_out=True)
    if amount and amount != 'None':
        amount = int(amount)
        return Announcement.query.filter(Announcement.amount >= amount, Announcement.open).order_by(order). \
            paginate(per_page=5, page=page_num, error_out=True)
    return Announcement.query.filter_by(open=True).order_by(order).paginate(per_page=5, page=page_num,
                                                                            error_out=True)
