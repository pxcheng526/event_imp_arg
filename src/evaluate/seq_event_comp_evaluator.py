from event_comp_evaluator import EventCompositionEvaluator
from seq_base_evaluator import SeqBaseEvaluator


class SeqEventCompositionEvaluator(SeqBaseEvaluator, EventCompositionEvaluator):
    def __init__(self, logger=None, use_lemma=True, include_type=True,
                 ignore_first_mention=False, filter_stop_events=True,
                 filter_repetitive_prep=True, use_max_score=True):
        super(SeqEventCompositionEvaluator, self).__init__(
            logger=logger,
            use_lemma=use_lemma,
            include_type=include_type,
            ignore_first_mention=ignore_first_mention,
            filter_stop_events=filter_stop_events,
            filter_repetitive_prep=filter_repetitive_prep
        )
        self.use_max_score = use_max_score
        self.model_name = 'event_composition (sequential)'

    def evaluate_event_list(self, rich_event_list):
        pos_input_all_list = [
            rich_event.get_pos_input_all() for rich_event in rich_event_list]

        for event_idx, rich_event in enumerate(rich_event_list):
            if event_idx == 0:
                continue

            self.logger.debug('Processing event #{}'.format(event_idx))
            if self.stop_pred_ids and \
                    rich_event.rich_pred.get_wv() in self.stop_pred_ids:
                continue

            context_input_list = \
                [pos_input for pos_input_all in pos_input_all_list[:event_idx]
                 for pos_input in pos_input_all]

            eval_input_list_all = rich_event.get_eval_input_list_all(
                include_salience=True)
            for rich_arg, eval_input_list in eval_input_list_all:
                if not self.ignore_argument(rich_arg):
                    most_coherent_idx = self.get_most_coherent(
                        rich_arg.arg_type, eval_input_list, context_input_list,
                        self.use_max_score)
                    correct = (most_coherent_idx == rich_arg.get_target_idx())
                    num_choices = len(eval_input_list)

                    kwargs = SeqBaseEvaluator.get_arg_group_info(rich_arg)

                    self.eval_stats.add_eval_result(
                        correct,
                        num_choices,
                        **kwargs
                    )
                    self.logger.debug(
                        'Processing {}, correct = {}, num_choices = {}'.format(
                            rich_arg.arg_type, correct, num_choices))