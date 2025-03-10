Token-based authentication

When using the REST interface, some AI services support (or even require) token-based authentication. In these cases, the subscription key is presented in an initial request to obtain an authentication token, which has a valid period of 10 minutes. Subsequent requests must present the token to validate that the caller has been authenticated.
========================================================
Introduction

In machine learning, models are trained to predict unknown labels for new data based on correlations between known labels and features found in the training data. Depending on the algorithm used, you may need to specify hyperparameters to configure how the model is trained.

For example, the logistic regression algorithm uses a regularization rate hyperparameter to counteract overfitting; and deep learning techniques for convolutional neural networks (CNNs) use hyperparameters like learning rate to control how weights are adjusted during training, and batch size to determine how many data items are included in each training batch.

 Note

Machine Learning is an academic field with its own particular terminology. Data scientists refer to the values determined from the training features as parameters, so a different term is required for values that are used to configure training behavior but which are not derived from the training data - hence the term hyperparameter.

The choice of hyperparameter values can significantly affect the resulting model, making it important to select the best possible values for your particular data and predictive performance goals.

Tuning hyperparameters
Diagram of different hyperparameter values resulting in different models by performing hyperparameter tuning.

Hyperparameter tuning is accomplished by training the multiple models, using the same algorithm and training data but different hyperparameter values. The resulting model from each training run is then evaluated to determine the performance metric for which you want to optimize (for example, accuracy), and the best-performing model is selected.

In Azure Machine Learning, you can tune hyperparameters by submitting a script as a sweep job. A sweep job will run a trial for each hyperparameter combination to be tested. Each trial uses a training script with parameterized hyperparameter values to train a model, and logs the target performance metric achieved by the trained model.

Learning objectives
In this module, you'll learn how to:


Define a hyperparameter search space.
Configure hyperparameter sampling.
Select an early-termination policy.
Run a sweep job.


Define a search space
Completed
100 XP
5 minutes
The set of hyperparameter values tried during hyperparameter tuning is known as the search space. The definition of the range of possible values that can be chosen depends on the type of hyperparameter.

Discrete hyperparameters
Some hyperparameters require discrete values - in other words, you must select the value from a particular finite set of possibilities. You can define a search space for a discrete parameter using a Choice from a list of explicit values, which you can define as a Python list (Choice(values=[10,20,30])), a range (Choice(values=range(1,10))), or an arbitrary set of comma-separated values (Choice(values=(30,50,100)))

You can also select discrete values from any of the following discrete distributions:

QUniform(min_value, max_value, q): Returns a value like round(Uniform(min_value, max_value) / q) * q
QLogUniform(min_value, max_value, q): Returns a value like round(exp(Uniform(min_value, max_value)) / q) * q
QNormal(mu, sigma, q): Returns a value like round(Normal(mu, sigma) / q) * q
QLogNormal(mu, sigma, q): Returns a value like round(exp(Normal(mu, sigma)) / q) * q
Continuous hyperparameters
Some hyperparameters are continuous - in other words you can use any value along a scale, resulting in an infinite number of possibilities. To define a search space for these kinds of value, you can use any of the following distribution types:

Uniform(min_value, max_value): Returns a value uniformly distributed between min_value and max_value
LogUniform(min_value, max_value): Returns a value drawn according to exp(Uniform(min_value, max_value)) so that the logarithm of the return value is uniformly distributed
Normal(mu, sigma): Returns a real value that's normally distributed with mean mu and standard deviation sigma
LogNormal(mu, sigma): Returns a value drawn according to exp(Normal(mu, sigma)) so that the logarithm of the return value is normally distributed
Defining a search space
To define a search space for hyperparameter tuning, create a dictionary with the appropriate parameter expression for each named hyperparameter.

For example, the following search space indicates that the batch_size hyperparameter can have the value 16, 32, or 64, and the learning_rate hyperparameter can have any value from a normal distribution with a mean of 10 and a standard deviation of 3.

Python

Copy
from azure.ai.ml.sweep import Choice, Normal

command_job_for_sweep = job(
    batch_size=Choice(values=[16, 32, 64]),    
    learning_rate=Normal(mu=10, sigma=3),
)


Configure a sampling method
Completed
100 XP
8 minutes
The specific values used in a hyperparameter tuning run, or sweep job, depend on the type of sampling used.

There are three main sampling methods available in Azure Machine Learning:

Grid sampling: Tries every possible combination.
Random sampling: Randomly chooses values from the search space.
Sobol: Adds a seed to random sampling to make the results reproducible.
Bayesian sampling: Chooses new values based on previous results.
 Note

Sobol is a variation of random sampling.

Grid sampling
Grid sampling can only be applied when all hyperparameters are discrete, and is used to try every possible combination of parameters in the search space.

For example, in the following code example, grid sampling is used to try every possible combination of discrete batch_size and learning_rate value:

Python

Copy
from azure.ai.ml.sweep import Choice

command_job_for_sweep = command_job(
    batch_size=Choice(values=[16, 32, 64]),
    learning_rate=Choice(values=[0.01, 0.1, 1.0]),
)

sweep_job = command_job_for_sweep.sweep(
    sampling_algorithm = "grid",
    ...
)
Random sampling
Random sampling is used to randomly select a value for each hyperparameter, which can be a mix of discrete and continuous values as shown in the following code example:

Python

Copy
from azure.ai.ml.sweep import Normal, Uniform

command_job_for_sweep = command_job(
    batch_size=Choice(values=[16, 32, 64]),   
    learning_rate=Normal(mu=10, sigma=3),
)

sweep_job = command_job_for_sweep.sweep(
    sampling_algorithm = "random",
    ...
)
Sobol
You may want to be able to reproduce a random sampling sweep job. If you expect that you do, you can use Sobol instead. Sobol is a type of random sampling that allows you to use a seed. When you add a seed, the sweep job can be reproduced, and the search space distribution is spread more evenly.

The following code example shows how to use Sobol by adding a seed and a rule, and using the RandomSamplingAlgorithm class:

Python

Copy
from azure.ai.ml.sweep import RandomSamplingAlgorithm

sweep_job = command_job_for_sweep.sweep(
    sampling_algorithm = RandomSamplingAlgorithm(seed=123, rule="sobol"),
    ...
)
Bayesian sampling
Bayesian sampling chooses hyperparameter values based on the Bayesian optimization algorithm, which tries to select parameter combinations that will result in improved performance from the previous selection. The following code example shows how to configure Bayesian sampling:

Python

Copy
from azure.ai.ml.sweep import Uniform, Choice

command_job_for_sweep = job(
    batch_size=Choice(values=[16, 32, 64]),    
    learning_rate=Uniform(min_value=0.05, max_value=0.1),
)

sweep_job = command_job_for_sweep.sweep(
    sampling_algorithm = "bayesian",
    ...
)
You can only use Bayesian sampling with choice, uniform, and quniform parameter expressions.


Configure early termination
Completed
100 XP
8 minutes
Hyperparameter tuning helps you fine-tune your model and select the hyperparameter values that will make your model perform best.

For you to find the best model, however, can be a never-ending conquest. You always have to consider whether it's worth the time and expense of testing new hyperparameter values to find a model that may perform better.

Each trial in a sweep job, a new model is trained with a new combination of hyperparameter values. If training a new model doesn't result in a significantly better model, you may want to stop the sweep job and use the model that performed best so far.

When you configure a sweep job in Azure Machine Learning, you can also set a maximum number of trials. A more sophisticated approach may be to stop a sweep job when newer models don't produce significantly better results. To stop a sweep job based on the performance of the models, you can use an early termination policy.

When to use an early termination policy
Whether you want to use an early termination policy may depend on the search space and sampling method you're working with.

For example, you may choose to use a grid sampling method over a discrete search space that results in a maximum of six trials. With six trials, a maximum of six models will be trained and an early termination policy may be unnecessary.

An early termination policy can be especially beneficial when working with continuous hyperparameters in your search space. Continuous hyperparameters present an unlimited number of possible values to choose from. You'll most likely want to use an early termination policy when working with continuous hyperparameters and a random or Bayesian sampling method.

Configure an early termination policy
There are two main parameters when you choose to use an early termination policy:

evaluation_interval: Specifies at which interval you want the policy to be evaluated. Every time the primary metric is logged for a trial counts as an interval.
delay_evaluation: Specifies when to start evaluating the policy. This parameter allows for at least a minimum of trials to complete without an early termination policy affecting them.
New models may continue to perform only slightly better than previous models. To determine the extent to which a model should perform better than previous trials, there are three options for early termination:

Bandit policy: Uses a slack_factor (relative) or slack_amount(absolute). Any new model must perform within the slack range of the best performing model.
Median stopping policy: Uses the median of the averages of the primary metric. Any new model must perform better than the median.
Truncation selection policy: Uses a truncation_percentage, which is the percentage of lowest performing trials. Any new model must perform better than the lowest performing trials.
Bandit policy
You can use a bandit policy to stop a trial if the target performance metric underperforms the best trial so far by a specified margin.

For example, the following code applies a bandit policy with a delay of five trials, evaluates the policy at every interval, and allows an absolute slack amount of 0.2.

Python

Copy
from azure.ai.ml.sweep import BanditPolicy

sweep_job.early_termination = BanditPolicy(
    slack_amount = 0.2, 
    delay_evaluation = 5, 
    evaluation_interval = 1
)
Imagine the primary metric is the accuracy of the model. When after the first five trials, the best performing model has an accuracy of 0.9, any new model needs to perform better than (0.9-0.2) or 0.7. If the new model's accuracy is higher than 0.7, the sweep job will continue. If the new model has an accuracy score lower than 0.7, the policy will terminate the sweep job.

Diagram of two examples when using a bandit policy: one model performs sufficiently good, the other underperforms.

You can also apply a bandit policy using a slack factor, which compares the performance metric as a ratio rather than an absolute value.

Median stopping policy
A median stopping policy abandons trials where the target performance metric is worse than the median of the running averages for all trials.

For example, the following code applies a median stopping policy with a delay of five trials and evaluates the policy at every interval.

Python

Copy
from azure.ai.ml.sweep import MedianStoppingPolicy

sweep_job.early_termination = MedianStoppingPolicy(
    delay_evaluation = 5, 
    evaluation_interval = 1
)
Imagine the primary metric is the accuracy of the model. When the accuracy is logged for the sixth trial, the metric needs to be higher than the median of the accuracy scores so far. Suppose the median of the accuracy scores so far is 0.82. If the new model's accuracy is higher than 0.82, the sweep job will continue. If the new model has an accuracy score lower than 0.82, the policy will stop the sweep job, and no new models will be trained.

Diagram of two examples when using a median stopping policy: one model performs sufficiently good, the other underperforms.

Truncation selection policy
A truncation selection policy cancels the lowest performing X% of trials at each evaluation interval based on the truncation_percentage value you specify for X.

For example, the following code applies a truncation selection policy with a delay of four trials, evaluates the policy at every interval, and uses a truncation percentage of 20%.

Python

Copy
from azure.ai.ml.sweep import TruncationSelectionPolicy

sweep_job.early_termination = TruncationSelectionPolicy(
    evaluation_interval=1, 
    truncation_percentage=20, 
    delay_evaluation=4 
)
Imagine the primary metric is the accuracy of the model. When the accuracy is logged for the fifth trial, the metric should not be in the worst 20% of the trials so far. In this case, 20% translates to one trial. In other words, if the fifth trial is not the worst performing model so far, the sweep job will continue. If the fifth trial has the lowest accuracy score of all trials so far, the sweep job will stop.

Use a sweep job for hyperparameter tuning
Completed
100 XP
8 minutes
In Azure Machine Learning, you can tune hyperparameters by running a sweep job.

Create a training script for hyperparameter tuning
To run a sweep job, you need to create a training script just the way you would do for any other training job, except that your script must:

Include an argument for each hyperparameter you want to vary.
Log the target performance metric with MLflow. A logged metric enables the sweep job to evaluate the performance of the trials it initiates, and identify the one that produces the best performing model.
 Note

Learn how to track machine learning experiments and models with MLflow within Azure Machine Learning.

For example, the following example script trains a logistic regression model using a --regularization argument to set the regularization rate hyperparameter, and logs the accuracy metric with the name Accuracy:

Python

Copy
import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import mlflow

# get regularization hyperparameter
parser = argparse.ArgumentParser()
parser.add_argument('--regularization', type=float, dest='reg_rate', default=0.01)
args = parser.parse_args()
reg = args.reg_rate

# load the training dataset
data = pd.read_csv("data.csv")

# separate features and labels, and split for training/validatiom
X = data[['feature1','feature2','feature3','feature4']].values
y = data['label'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30)

# train a logistic regression model with the reg hyperparameter
model = LogisticRegression(C=1/reg, solver="liblinear").fit(X_train, y_train)

# calculate and log accuracy
y_hat = model.predict(X_test)
acc = np.average(y_hat == y_test)
mlflow.log_metric("Accuracy", acc)
Configure and run a sweep job
To prepare the sweep job, you must first create a base command job that specifies which script to run and defines the parameters used by the script:

Python

Copy
from azure.ai.ml import command

# configure command job as base
job = command(
    code="./src",
    command="python train.py --regularization ${{inputs.reg_rate}}",
    inputs={
        "reg_rate": 0.01,
    },
    environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu@latest",
    compute="aml-cluster",
    )
You can then override your input parameters with your search space:

Python

Copy
from azure.ai.ml.sweep import Choice

command_job_for_sweep = job(
    reg_rate=Choice(values=[0.01, 0.1, 1]),
)
Finally, call sweep() on your command job to sweep over your search space:

Python

Copy
from azure.ai.ml import MLClient

# apply the sweep parameter to obtain the sweep_job
sweep_job = command_job_for_sweep.sweep(
    compute="aml-cluster",
    sampling_algorithm="grid",
    primary_metric="Accuracy",
    goal="Maximize",
)

# set the name of the sweep job experiment
sweep_job.experiment_name="sweep-example"

# define the limits for this sweep
sweep_job.set_limits(max_total_trials=4, max_concurrent_trials=2, timeout=7200)

# submit the sweep
returned_sweep_job = ml_client.create_or_update(sweep_job)
Monitor and review sweep jobs
You can monitor sweep jobs in Azure Machine Learning studio. The sweep job will initiate trials for each hyperparameter combination to be tried. For each trial, you can review all logged metrics.

Additionally, you can evaluate and compare models by visualizing the trials in the studio. You can adjust each chart to show and compare the hyperparameter values and metrics for each trial.

=======================================

Create a pipeline
Completed
100 XP
6 minutes
In Azure Machine Learning, a pipeline is a workflow of machine learning tasks in which each task is defined as a component.

Components can be arranged sequentially or in parallel, enabling you to build sophisticated flow logic to orchestrate machine learning operations. Each component can be run on a specific compute target, making it possible to combine different types of processing as required to achieve an overall goal.

A pipeline can be executed as a process by running the pipeline as a pipeline job. Each component is executed as a child job as part of the overall pipeline job.

Build a pipeline
An Azure Machine Learning pipeline is defined in a YAML file. The YAML file includes the pipeline job name, inputs, outputs, and settings.

You can create the YAML file, or use the @pipeline() function to create the YAML file.

 Tip

Review the reference documentation for the @pipeline() function.

For example, if you want to build a pipeline that first prepares the data, and then trains the model, you can use the following code:

Python

Copy
from azure.ai.ml.dsl import pipeline

@pipeline()
def pipeline_function_name(pipeline_job_input):
    prep_data = loaded_component_prep(input_data=pipeline_job_input)
    train_model = loaded_component_train(training_data=prep_data.outputs.output_data)

    return {
        "pipeline_job_transformed_data": prep_data.outputs.output_data,
        "pipeline_job_trained_model": train_model.outputs.model_output,
    }
To pass a registered data asset as the pipeline job input, you can call the function you created with the data asset as input:

Python

Copy
from azure.ai.ml import Input
from azure.ai.ml.constants import AssetTypes

pipeline_job = pipeline_function_name(
    Input(type=AssetTypes.URI_FILE, 
    path="azureml:data:1"
))
The @pipeline() function builds a pipeline consisting of two sequential steps, represented by the two loaded components.

To understand the pipeline built in the example, let's explore it step by step:

The pipeline is built by defining the function pipeline_function_name.
The pipeline function expects pipeline_job_input as the overall pipeline input.
The first pipeline step requires a value for the input parameter input_data. The value for the input will be the value of pipeline_job_input.
The first pipeline step is defined by the loaded component for prep_data.
The value of the output_data of the first pipeline step is used for the expected input training_data of the second pipeline step.
The second pipeline step is defined by the loaded component for train_model and results in a trained model referred to by model_output.
Pipeline outputs are defined by returning variables from the pipeline function. There are two outputs:
pipeline_job_transformed_data with the value of prep_data.outputs.output_data
pipeline_job_trained_model with the value of train_model.outputs.model_output
Diagram of pipeline structure including all inputs and outputs.

The result of running the @pipeline() function is a YAML file that you can review by printing the pipeline_job object you created when calling the function:

Python

Copy
print(pipeline_job)
The output will be formatted as a YAML file, which includes the configuration of the pipeline and its components. Some parameters included in the YAML file are shown in the following example.

yml

Copy
display_name: pipeline_function_name
type: pipeline
inputs:
  pipeline_job_input:
    type: uri_file
    path: azureml:data:1
outputs:
  pipeline_job_transformed_data: null
  pipeline_job_trained_model: null
jobs:
  prep_data:
    type: command
    inputs:
      input_data:
        path: ${{parent.inputs.pipeline_job_input}}
    outputs:
      output_data: ${{parent.outputs.pipeline_job_transformed_data}}
  train_model:
    type: command
    inputs:
      input_data:
        path: ${{parent.outputs.pipeline_job_transformed_data}}
    outputs:
      output_model: ${{parent.outputs.pipeline_job_trained_model}}
tags: {}
properties: {}
settings: {}

=============

Introduction

Foundation models, such as GPT-3, are state-of-the-art natural language processing models designed to understand, generate, and interact with human language. To understand the significance of foundation models, it's essential to explore their origins, which stem from advancements in the fields of artificial intelligence and natural language processing.

Understand artificial intelligence
Diagram visualizing the relationship between artificial intelligence, machine learning, and deep learning.

The purpose of artificial intelligence (AI) is for computers or machines to perform tasks with human-like intelligence.
A popular approach nowadays to approach artificial intelligence is through machine learning, a subfield that gives computers the ability to learn without being explicitly programmed.
The subfield of deep learning uses artificial neural networks to learn and represent complex patterns and hierarchies from data, which are especially useful for data like images and text.
In other words, machine learning and deep learning techniques can be used to realize AI. There are different types of tasks that you can have computers or machines perform.

Understand natural language processing
Natural language processing (NLP) is a type of AI that focuses on understanding, interpreting, and generating human language. Some common NLP use cases are:

Diagram visualizing six common use cases for natural language processing tasks.

Speech-to-text and text-to-speech conversion. For example, generate subtitles for videos.
Machine translation. For example, translate text from English to Japanese.
Text classification. For example, label an email as spam or not spam.
Entity extraction. For example, extract keywords or names from a document.
Question answering. For example, provide answers to questions like "What is the capital of France?"
Text summarization. For example, generate a short one-paragraph summary from a multi-page document.
Historically, NLP has been challenging as our language is complex and computers find it hard to understand text. In this module, you learn how developments in AI and specifically NLP have led to the models we use today. You'll explore and use various language models in the model catalog, available in the Azure Machine Learning studio.

===========================================================
Array Map
One of the important methods on the Array prototype is map. Map allows you take each element of an array and apply a function to it, returning the result after the function.

Let's say we had a function that adds one to an element:

addOne

Simple enough function. We take a number, add one to it and return it. Input 3, output 4.

What if we wanted to apply this function to several elements? We can do so using map!

map

Now we take our addOne function and we map it over each element. Every element will go through the function and return the resulting element. Input 3, output 4. Input 4, output 5 etc...

Or in code:

const arr = [3,4,5];

const newArr = arr.map(function(x) {
    return x + 1;
});

console.log( newArr ); // [4,5,6]
