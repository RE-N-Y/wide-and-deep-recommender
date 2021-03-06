#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import argparse
from datetime import datetime
import multiprocessing
import tensorflow as tf
import model
import metadata

def serving_input():
    csv_row = tf.placeholder(
        shape=[None],
        dtype=tf.string
    )

    features = dict(zip(metadata.column,parse_csv(csv_row[:-1],serving=True)))
    return tf.estimator.export.ServingInputReceiver(
        features=features,
        receiver_tensors={'csv_row':csv_row}
    )

def parse_csv(csv_string,serving=False):
    feature_size = metadata.META_DATA["full_feature_size"]
    if serving:
        feature_size-=1
    record_defaults = [[0.0]] * feature_size
    return tf.decode_csv(csv_string,record_defaults=record_defaults)

def generate_input_fn(file_names,mode=tf.estimator.ModeKeys.EVAL,shuffle=True,num_epochs=10,batch_size=100,multi_threading=True):
    def _generate_input_fn():
        shuffle = True if mode == tf.estimator.ModeKeys.TRAIN else False
        num_threads = multiprocessing.cpu_count() if multi_threading else 1
        buffer_size = 2 * batch_size + 1

        print("")
        print("* data input_fn:")
        print("================")
        print("Mode: {}".format(mode))
        print("Input file(s): {}".format(file_names))
        print("Batch size: {}".format(batch_size))
        print("Epoch count: {}".format(num_epochs))
        print("Thread count: {}".format(num_threads))
        print("Shuffle: {}".format(shuffle))
        print("================")
        print("")

        
        dataset = tf.data.TextLineDataset(file_names)
        dataset = dataset.map(lambda e: parse_csv(e))
        if shuffle:
            dataset = dataset.shuffle(buffer_size)
            
        dataset = dataset.batch(batch_size)
        dataset = dataset.prefetch(buffer_size)
        dataset = dataset.repeat(num_epochs)

        iterator = dataset.make_one_shot_iterator()
        next_input = list(iterator.get_next())
        target = tf.transpose(next_input[-1:])
        features = dict(zip(metadata.column,next_input[:-1]))

        return features, target

    return _generate_input_fn

# ******************************************************************************
# YOU MAY MODIFY THIS FUNCTION TO ADD/REMOVE PARAMS OR CHANGE THE DEFAULT VALUES
# ******************************************************************************


def initialise_hyper_params(args_parser):
    """
    Define the arguments with the default values,
    parses the arguments passed to the task,
    and set the HYPER_PARAMS global variable

    Args:
        args_parser
    """

    # Data files arguments
    args_parser.add_argument(
        '--train-files',
        help='GCS or local paths to training data',
        nargs='+',
        required=True
    )
    args_parser.add_argument(
        '--eval-files',
        help='GCS or local paths to evaluation data',
        nargs='+',
        required=True
    )
    args_parser.add_argument(
        '--feature-stats-file',
        help='GCS or local paths to feature statistics json file',
        nargs='+',
        default=None
    )
    ###########################################

    # Experiment arguments - training
    args_parser.add_argument(
        '--train-steps',
        help="""
        Steps to run the training job for. If --num-epochs and --train-size are not specified,
        this must be. Otherwise the training job will run indefinitely.
        if --num-epochs and --train-size are specified, then --train-steps will be:
        (train-size/train-batch-size) * num-epochs\
        """,
        default=1000,
        type=int
    )
    args_parser.add_argument(
        '--train-batch-size',
        help='Batch size for each training step',
        type=int,
        default=200
    )
    args_parser.add_argument(
        '--train-size',
        help='Size of training set (instance count)',
        type=int,
        default=None
    )
    args_parser.add_argument(
        '--num-epochs',
        help="""\
        Maximum number of training data epochs on which to train.
        If both --train-size and --num-epochs are specified,
        --train-steps will be: (train-size/train-batch-size) * num-epochs.\
        """,
        default=400,
        type=int,
    )
    ###########################################

    # Experiment arguments - evaluation
    args_parser.add_argument(
        '--eval-every-secs',
        help='How long to wait before running the next evaluation',
        default=120,
        type=int
    )
    args_parser.add_argument(
        '--eval-steps',
        help="""\
        Number of steps to run evaluation for at each checkpoint',
        Set to None to evaluate on the whole evaluation data
        """,
        default=None,
        type=int
    )
    args_parser.add_argument(
        '--eval-batch-size',
        help='Batch size for evaluation steps',
        type=int,
        default=200
    )
    ###########################################

    # Features processing arguments
    args_parser.add_argument(
        '--num-buckets',
        help='Number of buckets into which to discretize numeric columns',
        default=10,
        type=int
    )
    args_parser.add_argument(
        '--embedding-size',
        help='Number of embedding dimensions for categorical columns. value of 0 means no embedding',
        default=4,
        type=int
    )
    ###########################################

    # Estimator arguments
    args_parser.add_argument(
        '--learning-rate',
        help="Learning rate value for the optimizers",
        default=0.001,
        type=float
    )
    args_parser.add_argument(
        '--learning-rate-decay-factor',
        help="""\
             **VALID FOR CUSTOM MODELS**
             The factor by which the learning rate should decay by the end of the training.
             decayed_learning_rate = learning_rate * decay_rate ^ (global_step / decay_steps)
             If set to 1.0 (default), then no decay will occur
             If set to 0.5, then the learning rate should reach 0.5 of its original value at the end of the training. 
             Note that, decay_steps is set to train_steps\
             """,
        default=1.0,
        type=float
    )
    args_parser.add_argument(
        '--hidden-units',
        help="""\
             Hidden layer sizes to use for DNN feature columns, provided in comma-separated layers. 
             If --scale-factor > 0, then only the size of the first layer will be used to compute 
             the sizes of subsequent layers \
             """,
        default='1024,512,256'
    )
    args_parser.add_argument(
        '--layer-sizes-scale-factor',
        help="""\
            Determine how the size of the layers in the DNN decays. 
            If value = 0 then the provided --hidden-units will be taken as is\
            """,
        default=0.7,
        type=float
    )
    args_parser.add_argument(
        '--num-layers',
        help='Number of layers in the DNN. If --scale-factor > 0, then this parameter is ignored',
        default=4,
        type=int
    )
    args_parser.add_argument(
        '--dropout-prob',
        help="The probability we will drop out a given coordinate",
        default=None
    )
    args_parser.add_argument(
        '--encode-one-hot',
        help="""\
        If set to True, the categorical columns will be encoded as One-Hot indicators in the deep part of the DNN model.
        Otherwise, the categorical columns will only be used in the wide part of the DNN model
        """,
        action='store_true',
        default=True,
    )
    args_parser.add_argument(
        '--as-wide-columns',
        help="""\
        If set to True, the categorical columns will be used in the wide part of the DNN model
        """,
        action='store_true',
        default=True,
    )
    args_parser.add_argument(
        '--l2-regularization',
        help="""\
        l2-regularization constant for training
        """,
        default=0.01
    )
    args_parser.add_argument(
        '--l1-regularlization',
        help="""\
        l1-regularlization constant for training
        """,
        default=0.01
    )
    ###########################################

    # Saved model arguments
    args_parser.add_argument(
        '--job-dir',
        help='GCS location to write checkpoints and export models',
        required=True
    )
    args_parser.add_argument(
        '--reuse-job-dir',
        action='store_true',
        default=False,
        help="""\
            Flag to decide if the model checkpoint should
            be re-used from the job-dir. If False then the
            job-dir will be deleted"""
    )
    args_parser.add_argument(
        '--export-format',
        help='The input format of the exported SavedModel binary',
        choices=['JSON', 'CSV', 'EXAMPLE'],
        default='CSV'
    )
    ###########################################

    # Argument to turn on all logging
    args_parser.add_argument(
        '--verbosity',
        choices=[
            'DEBUG',
            'ERROR',
            'FATAL',
            'INFO',
            'WARN'
        ],
        default='INFO',
    )

    return args_parser.parse_args()


# ******************************************************************************
# YOU NEED NOT TO CHANGE THE FUNCTION TO RUN THE EXPERIMENT
# ******************************************************************************


def run_experiment(run_config):
    """Train, evaluate, and export the model using tf.estimator.train_and_evaluate API"""

    train_input_fn = generate_input_fn(
        file_names=HYPER_PARAMS.train_files,
        mode=tf.estimator.ModeKeys.TRAIN,
        num_epochs=HYPER_PARAMS.num_epochs,
        batch_size=HYPER_PARAMS.train_batch_size
    )

    eval_input_fn = generate_input_fn(
        file_names=HYPER_PARAMS.eval_files,
        mode=tf.estimator.ModeKeys.EVAL,
        batch_size=HYPER_PARAMS.eval_batch_size,
    )

    exporter = tf.estimator.FinalExporter(
        'estimator',
        serving_input,
        as_text=False  # change to true if you want to export the model as readable text
    )

    # compute the number of training steps based on num_epoch, train_size, and train_batch_size
    if HYPER_PARAMS.train_size is not None and HYPER_PARAMS.num_epochs is not None:
        train_steps = (HYPER_PARAMS.train_size / HYPER_PARAMS.train_batch_size) * \
                      HYPER_PARAMS.num_epochs
    else:
        train_steps = HYPER_PARAMS.train_steps

    train_spec = tf.estimator.TrainSpec(
        train_input_fn,
        max_steps=int(train_steps)
    )
    print(int(train_steps))
    eval_spec = tf.estimator.EvalSpec(
        eval_input_fn,
        steps=HYPER_PARAMS.eval_steps,
        exporters=[exporter],
        throttle_secs=HYPER_PARAMS.eval_every_secs,
    )
    print(HYPER_PARAMS.eval_steps)
    def metric_fn(labels,predictions):
        metrics = {
            'mse': tf.metrics.mean_squared_error(labels,predictions['predictions'])
        }
        return metrics

    print("* experiment configurations")
    print("===========================")
    print("Train size: {}".format(HYPER_PARAMS.train_size))
    print("Epoch count: {}".format(HYPER_PARAMS.num_epochs))
    print("Train batch size: {}".format(HYPER_PARAMS.train_batch_size))
    print("Training steps: {} ({})".format(int(train_steps),
                                           "supplied" if HYPER_PARAMS.train_size is None else "computed"))
    print("Evaluate every {} seconds".format(HYPER_PARAMS.eval_every_secs))
    print("===========================")

    estimator = model.create_estimator(
        config=run_config
    )
    estimator = tf.contrib.estimator.add_metrics(estimator, metric_fn)
    # train and evaluate
    tf.estimator.train_and_evaluate(
        estimator,
        train_spec,
        eval_spec
    )


# ******************************************************************************
# THIS IS ENTRY POINT FOR THE TRAINER TASK
# ******************************************************************************


def main():

    print('')
    print('Hyper-parameters:')
    print(HYPER_PARAMS)
    print('')

    # Set python level verbosity
    tf.logging.set_verbosity(HYPER_PARAMS.verbosity)

    # Set C++ Graph Execution level verbosity
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = str(tf.logging.__dict__[HYPER_PARAMS.verbosity] / 10)

    # Directory to store output model and checkpoints
    model_dir = HYPER_PARAMS.job_dir

    # If job_dir_reuse is False then remove the job_dir if it exists
    print("Resume training:", HYPER_PARAMS.reuse_job_dir)
    if not HYPER_PARAMS.reuse_job_dir:
        if tf.gfile.Exists(model_dir):
            tf.gfile.DeleteRecursively(model_dir)
            print("Deleted job_dir {} to avoid re-use".format(model_dir))
        else:
            print("No job_dir available to delete")
    else:
        print("Reusing job_dir {} if it exists".format(model_dir))

    run_config = tf.estimator.RunConfig(
        tf_random_seed=19830610,
        log_step_count_steps=1000,
        save_checkpoints_secs=120,  # change if you want to change frequency of saving checkpoints
        keep_checkpoint_max=3,
        model_dir=model_dir
    )

    run_config = run_config.replace(model_dir=model_dir)
    print("Model Directory:", run_config.model_dir)

    # Run the train and evaluate experiment
    time_start = datetime.utcnow()
    print("")
    print("Experiment started at {}".format(time_start.strftime("%H:%M:%S")))
    print(".......................................")

    run_experiment(run_config)

    time_end = datetime.utcnow()
    print(".......................................")
    print("Experiment finished at {}".format(time_end.strftime("%H:%M:%S")))
    print("")
    time_elapsed = time_end - time_start
    print("Experiment elapsed time: {} seconds".format(time_elapsed.total_seconds()))
    print("")


args_parser = argparse.ArgumentParser()
HYPER_PARAMS = initialise_hyper_params(args_parser)

if __name__ == '__main__':
    main()
