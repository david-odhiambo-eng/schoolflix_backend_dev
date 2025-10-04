from tortoise import fields, models
import uuid


class Campus(models.Model):
    id = fields.UUIDField(pk=True, db_index=True, unique=True, default=uuid.uuid4)
    name = fields.CharField(max_length=100, unique=True)

    #students: fields.ReverseRelation["User"]

    class Meta:
        table = "campuses"
        app = "models" 
    @property
    def students(self):
        return self.students.all()


class User(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255, min_length=8)

    campus = fields.ForeignKeyField(
        "models.Campus",
        related_name="students",
        on_delete=fields.SET_NULL,
        null=True,
    )
    store= fields.ForeignKeyField(
        "stores.Shop",
        related_name="students_shop",
        on_delete=fields.SET_NULL,
        null=True,
    )

    class Meta:
        table = "users"
        app = "models"
