import click
from flask import Flask

from app.extensions import db
from app.models import AdminUser
from app.utils.security import hash_password


def register_commands(app: Flask) -> None:
    @app.cli.group("admin")
    def admin_group():
        """Admin management commands."""

    @admin_group.command("create-user")
    @click.option("--username", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option("--display-name", prompt=True)
    @click.option("--email", default=None)
    @click.option("--phone", default=None)
    def create_user(username, password, display_name, email, phone):
        if AdminUser.query.filter_by(username=username).first():
            raise click.ClickException("用户名已存在")

        user = AdminUser(
            username=username,
            password_hash=hash_password(password),
            display_name=display_name,
            email=email,
            phone=phone,
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        click.echo(f"已创建管理员账号: {username}")

