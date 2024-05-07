import logging
from typing import Any

from rouge_score import rouge_scorer

from moonshot.src.metrics.metric_interface import MetricInterface
from moonshot.src.utils.timeit import timeit

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RougeScorer(MetricInterface):
    def __init__(self):
        self.id = "rougescorer"
        self.name = "RougeScorer"
        self.description = "RougeScorer returns the various rouge scores."
        self.metric_config = self.get_metrics_configuration(self.id)

    @timeit
    def get_metadata(self) -> dict | None:
        """
        Retrieves and returns the metadata of the RougeScorer class.
        The metadata includes the unique identifier, the name, and the description of the class.

        Returns:
            dict | None: A dictionary containing the 'id', 'name', and 'description' of the RougeScorer class,
            or None if not applicable.
        """
        return {"id": self.id, "name": self.name, "description": self.description}

    @timeit
    async def get_results(
        self, prompts: Any, predicted_results: Any, targets: Any, *args, **kwargs
    ) -> dict:
        """
        Calculate the rouge scores for a given set of predicted results and target outputs.

        Args:
            prompts (Any): The prompts used to generate the predicted results.
            predicted_results (Any): The predicted results generated by the model.
            targets (Any): The target outputs to compare the predicted results against.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: A dictionary containing the rouge scores for each target-output pair, as well as the average scores.

        Raises:
            RuntimeError: If there is an exception during the calculation of the rouge scores.
        """
        try:
            # Define the test metrics to calculate
            test_metrics = ["rouge1", "rouge2", "rougeLsum"]

            # Initialize average recall, precision, and f-measure lists
            avg_recall = [0.0, 0.0, 0.0]
            avg_precision = [0.0, 0.0, 0.0]
            avg_fmeasure = [0.0, 0.0, 0.0]

            # Initialize the output dictionary and individual scores list
            output_dict = {}
            individual_scores = []

            # Calculate rouge scores for each target-output pair
            print("Attempting to calculate rouge score")
            scorer = rouge_scorer.RougeScorer(test_metrics)
            for target, result in zip(targets, predicted_results):
                scores = scorer.score(target, result)
                test_metrics_dict = {}
                for test_metric_index, test_metric in enumerate(test_metrics, 0):
                    # Store each individual rouge score to calculate average score
                    avg_recall[test_metric_index] += scores[test_metric].recall
                    avg_precision[test_metric_index] += scores[test_metric].precision
                    avg_fmeasure[test_metric_index] += scores[test_metric].fmeasure

                    # Store each individual rouge score
                    test_metrics_dict[test_metric] = {
                        "r": scores[test_metric].recall,
                        "p": scores[test_metric].precision,
                        "f": scores[test_metric].fmeasure,
                    }
                individual_scores.append(test_metrics_dict)

            # Add individual scores to the output dictionary
            output_dict["rouge-scores"] = individual_scores

            # Calculate average scores and add them to the output dictionary
            for avg_index, (recall, precision, fmeasure) in enumerate(
                zip(avg_recall, avg_precision, avg_fmeasure)
            ):
                output_dict[f"avg_{test_metrics[avg_index]}"] = {
                    "r": recall / len(targets),
                    "p": precision / len(targets),
                    "f": fmeasure / len(targets),
                }

            # Return the final rouge scores dictionary
            return {"rouge": output_dict}

        except Exception as exception:
            # Raise an error if there is an exception during calculation
            raise RuntimeError(f"Unable to calculate rouge score - {str(exception)}")
