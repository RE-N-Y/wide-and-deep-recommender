import tensorflow as tf
import task
import metadata

def to_numeric_feature_column(feature_list):
    feature_column_list = []
    for feature_name in feature_list:
        feature_column_list.append(tf.feature_column.numeric_column(feature_name))
    return feature_column_list

def construct_hidden_unit():
    hidden_units = list(map(int, task.HYPER_PARAMS.hidden_units.split(',')))
    return hidden_units

def create_estimator(config):

    wide_column = to_numeric_feature_column(metadata.user_column+metadata.anime_times_column+metadata.anime_genres_column+metadata.user_genres_column+metadata.user_times_column)
    deep_column = to_numeric_feature_column(metadata.user_characters_column + metadata.user_staffs_column + metadata.user_studios_column + metadata.anime_staffs_column + metadata.anime_characters_column + metadata.anime_studios_column + metadata.animes_topic_column)

    linear_optimizer = tf.train.FtrlOptimizer(
        learning_rate=task.HYPER_PARAMS.learning_rate,
        l1_regularization_strength=task.HYPER_PARAMS.l1_regularlization
    )

    dnn_optimizer = tf.train.AdamOptimizer(
        learning_rate=task.HYPER_PARAMS.learning_rate
    )

    estimator = tf.estimator.DNNLinearCombinedRegressor(
        linear_feature_columns=wide_column,
        linear_optimizer=linear_optimizer,
        dnn_feature_columns=deep_column,
        dnn_hidden_units=construct_hidden_unit(),
        dnn_optimizer=dnn_optimizer,
        dnn_dropout=task.HYPER_PARAMS.dropout_prob,
        batch_norm=True,
        config=config
    )
    
    return estimator
