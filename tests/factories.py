import factory

from apps.catalog.models import AnswerOption, Category, Question


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    slug = factory.Sequence(lambda n: f"kategori-{n}")
    name = factory.Sequence(lambda n: f"Kategori {n}")
    color_hex = "#6C4DFF"
    icon = "code"


class QuestionFactory(factory.django.DjangoModelFactory):
    """Tam 4 şık (ilki doğru) ile soru üretir."""

    class Meta:
        model = Question
        skip_postgeneration_save = True

    category = factory.SubFactory(CategoryFactory)
    text = factory.Sequence(lambda n: f"Soru {n}?")
    explanation = "Açıklama"

    @factory.post_generation
    def options(self, create, extracted, **kwargs):
        if not create:
            return
        for i in range(4):
            AnswerOption.objects.create(
                question=self, text=f"Şık {i}", is_correct=(i == 0), display_order=i
            )


def make_category_with_questions(count: int = 20, **kwargs) -> Category:
    category = CategoryFactory(**kwargs)
    QuestionFactory.create_batch(count, category=category)
    return category
