from django.db import models
from django.contrib.auth.models import User


class Breed(models.Model):
    name = models.CharField("Название породы", max_length=100)

    def __str__(self):
        return self.name


class Kitten(models.Model):
    name = models.CharField("Имя", max_length=100)
    color = models.CharField("Цвет", max_length=100)
    age_in_months = models.PositiveIntegerField("Возраст (в месяцах)")
    description = models.TextField("Описание")
    breed = models.ForeignKey(Breed, on_delete=models.CASCADE, verbose_name="Порода")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")

    def __str__(self):
        return self.name


class Rating(models.Model):
    kitten = models.ForeignKey(Kitten, on_delete=models.CASCADE, verbose_name="Котёнок")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.PositiveSmallIntegerField("Рейтинг")

    def __str__(self):
        return f"Rating {self.rating} for {self.kitten.name} by {self.user.username}"

    class Meta:
        unique_together = ('kitten', 'user')
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1, rating__lte=5), name='rating_range')
        ]
