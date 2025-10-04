from tortoise import models, fields

class Shop(models.Model):
    name: str = fields.CharField(max_length=100)
    students: fields.ReverseRelation['models.User']
    class Meta:
        table='shops'
        app='stores'
    def __str__(self):
        return f'{self.name}'
