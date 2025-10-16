"""
This shows how to use the SDK to build a simple product feedback summarization workflow.
"""

import pendulum

from typing import Literal, Any

from airflow.decorators import dag, task
from airflow.exceptions import AirflowSkipException

import airflow_ai_sdk as ai_sdk

@task
def get_product_feedback() -> list[str]:
    """
    This task returns a mocked list of product feedback. In a real workflow, this
    task would get the product feedback from a database or API.
    """
    return [
            "Absolutely blown away by this Speyside scotch. The nose is full of honey, toasted almonds, and a faint hint of spiced apple. The palate is even better, with a smooth, velvety texture and flavors of rich caramel, vanilla, and a nutty finish. It's a genuine pleasure to sip neat. Definitely a re-buy",
            "For the price, you simply can't beat this small-batch bourbon. It offers a surprising amount of complexity, with a nose of brown sugar and dried fruit. The taste has a nice kick of cinnamon and oak, ending with a long, warm finish. A fantastic everyday sipper",
            "Bought this rye on a whim and was happily surprised. It’s got a lovely spicy kick up front, but it’s beautifully balanced by notes of candied peaches and a creamy vanilla. The high rye content makes for a very flavorful and interesting pour",
            "This single malt has such a unique and memorable flavor profile. It starts with a burst of bright citrus and a touch of peat smoke, followed by layers of vanilla and malt. The finish is long, dry, and has a pleasant smoky brine. A truly excellent and sophisticated dram",
            "My new favorite! This wheated bourbon is incredibly smooth and easy to drink. The notes of graham cracker and toasted marshmallow on the nose are delightful, and the palate delivers rich vanilla and a hint of baked cherries. It's a dessert in a glass",
            "Got this as a gift for my husband, and he loves it! He said it has a lovely balance of sweetness and spice, with deep caramel and vanilla flavors. The bottle arrived quickly and was perfectly packaged. Might have to get one for myself",
            "Just finished my first bottle and already ordered another. It’s a very drinkable whiskey that works well in a cocktail or on its own. It's not a flavor bomb, but it's reliably smooth and well-rounded. Perfect for a relaxing evening",
            "A fantastic experience! The staff was knowledgeable and the whiskey selection was top-notch. The bourbon was creamy, with notes of oak and butterscotch. I'll definitely be using their services again",
            "I was positively surprised by this blend. The low price made me skeptical, but it’s much better than I expected. Cereal sweetness, caramel, and a hint of fruitiness—a simple but decent blended scotch",
            "This is an outstanding rye whiskey. It's thick and rich, with notes of black tea and orange zest that I really love. It's a bit of a splurge, but it's worth it for the complex and interesting taste. My new go-to",
            "This bourbon is a total crowd-pleaser. The nose offers sweet corn and brown sugar, while the palate has lovely notes of pecan and coffee. The finish is long and savory, with a hint of honeyed apple. Perfect for sharing with friends.",
            "I don't normally leave reviews, but this single barrel bourbon deserves one. It's consistently delicious, with cinnamon, caramel, and a pleasant minty note. I always grab a bottle when I see it",
            "Couldn’t even finish the glass. It smelled like rubbing alcohol and had a harsh, metallic taste that was just awful. Definitely not for sipping, and it ruined my cocktail. An absolute waste of money.",
            "What a disappointment. This whiskey is thin and lacks any character. Tastes like a mixture of watery caramel and burnt wood. The finish is short and leaves a bitter aftertaste. I won't be buying this brand again",
            "Ordered this bourbon hoping for a rich, flavorful experience, but it was just terrible. Tasted like wood chip water and was extremely unpleasant. Not even good enough for a mixer. They should be embarrassed to sell this.",
            "This has a very strange, off-putting taste, like a heavily chlorinated swimming pool mixed with something medicinal. It's intriguingly bad, but not in a way that makes you want to keep drinking it",
            "It's an okay whiskey. Nothing special, but not bad either. It's smooth enough, with some standard vanilla and caramel notes, but it lacks the depth and complexity I usually look for. A safe option, I guess.",
            "This whiskey is fine for mixing in a highball, but I wouldn't drink it neat. The flavor is a bit bland, and it gets a little thin at the end. It gets the job done without standing out in any way.",
            "This is a decent bourbon. It's got a classic bourbon profile—caramel, spice, and oak—but it doesn't do anything new or exciting. The finish is of average length and warmth. You get what you pay for.",
            "I was given this as a gift. It's definitely drinkable, but not something I would rush out to buy. It's a little hot and light on the palate. It's a perfectly acceptable and somewhat forgettable pour."
    ]

class ProductFeedbackSummary(ai_sdk.BaseModel):
    summary: str
    sentiment: Literal["positive", "negative", "neutral"]
    feature_requests: list[str]


@task.llm(model="gpt-4o-mini", result_type=ProductFeedbackSummary, system_prompt="Extract the summary, sentiment, and feature requests from the product feedback.",)
def summarize_product_feedback(feedback: str | None = None) -> ProductFeedbackSummary:
    """
    This task summarizes the product feedback. You can add logic here to transform the input
    before summarizing it.
    """
    # if the feedback doesn't mention Airflow, skip it
    #if "Airflow" not in feedback:
    #    raise AirflowSkipException("Feedback does not mention Airflow")

    return feedback


@task
def upload_summaries(summaries: list[dict[str, Any]]):
    """
    This task prints the summaries. In a real workflow, this task would upload the summaries to a database or API.
    """
    from pprint import pprint
    for summary in summaries:
        pprint(summary)

@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
)
def product_feedback_summarization():
    feedback = get_product_feedback()
    summaries = summarize_product_feedback.expand(feedback=feedback)
    upload_summaries(summaries)

dag = product_feedback_summarization()

if __name__ == "__main__":
    dag.test()
