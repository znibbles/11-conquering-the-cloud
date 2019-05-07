# 01 Serverless Audio Analysis with Google Cloud Functions and Librosa

Lately I've been tasked with running an audio feature extraction upon upload of sounds into some space on the web.

One of the benefits of today's cloud computing environment is that you don't need a full server stack to do this anymore. The buzzword "serverless", of course, doesn't mean that there are no servers involved anymore, rather, they're being kept behind the curtain. The benefits of such a setup are a more scalable, plannable, potentially more ecological way of using server resources, as you only pay for the usage (CPU time, storage) you actually need. On the downside, in reality you are limited to a few major platforms for setting up such an environment (the largest and most well-known are of course Amazon, Google and Microsoft), resulting in an even stronger monopolisation and vendor lock-in. There are initiatives like [OpenFaaS](https://github.com/openfaas/faas) trying to wrest this market power from the big ones, but then again you need to host it on your own server again, which only makes sense for bigger projects.

Anyway, what are the steps of creating such a _serverless_ setup?

1. We need a place where uploaded files can be stored. Most cloud providers call this a _bucket_.
2. If a file is uploaded into this bucket, a _function is triggered_. This function can (and in most cases will) have side effects like 
3. Storing some metadata in a _cloud database_.

We will be implementing all three of these steps in this video.

## Introducing Google Cloud Platform

I've chosen the Google Cloud Platform for this because it provides the simplest way of customizing a _Python_ environment, which we will need for our implementation. For the rest of this tutorial I will assume that you have a Google account and are familiar with the [Google Cloud Console](https://console.cloud.google.com). If not, there are a lot of  guides out there on how to set up an account.

First of all, we need to set up a new project. I will call this `znibbles-audio-analysis`, and wait a few seconds for the initialization to complete.

Next we are going to set up a bucket to hold our data. Scroll down to `Storage`, and click `Create Bucket`. We have to give it a unique name here, and select an appropriate location, else we can go with the defaults here.

## Setting up a Firestore Database

Let's create a `Firestore` database next. We have to choose between native and datastore mode, which is beyond the scope of this video, but in our case it doesn't really matter. We select a location, click `Create Database`, and off we go.

Now, we don't really need to do this because it will get created on demand, but let's just start a collection called `sounds` here. It also adds a default empty document, which we can delete.

## Devising a Google Cloud Function

Alright, now off to our analysis logic. Click `Cloud Functions` and enable the Cloud Functions API.

Next, click `Create function`. You will be presented with a form that asks for a function name and some other variables. Let's call it `analyze_audio`, and give it a little more RAM, just in case.

Next we need to set the trigger, and this is where our bucket comes in. We choose `Cloud Storage` and select the bucket we created before, after all we want the logic to run whenever an object is created in the bucket. For our runtime, we switch to `Python 3.7`.

The simplest way to add the function logic is to do it inline here, which I will do in this case for demonstration purposes.

First, let's add our _dependencies_ to `requirement.txt`. We are going to need `numpy`, the Python clients for Google's Cloud Storage and Firestore, as well as Librosa. This is a nice feat of the Google Cloud Platform - it will install these dependencies automatically for you. Last I checked, this wasn't so easy with Amazon and the other competitors.

## LibRosa

Let's take a quick look at `librosa`. It's a Python package for music and audio analysis, which is quite easy to use. From the _feature extraction_ list, we'll select the `MFCC` portion and save them to the database.

## Coding the Analysis Logic

Okay, back to our Python code. First, we rename the function to `analyze`. I'm going to enlarge this editor here. Let's start by extracting relevant information from the `event` dictionary. The exact contents of this collection depend on what trigger you choose - in our case we are interested in the filename and the bucket name.

Next we need to access the exact blob of the uploaded object, and for this we need Google's Storage Client. So we import `storage` from `google.cloud` and instantiate a `storage_client`. Now we ask it for the bucket using the `bucket_name`, get the blob associated with the `file_name`, and store the `blob_name` in a variable.

Since all function executions are ephemeral (meaning the runtime environment is completely discarded afterwards), we have to store our audio data in a temporary file. For this we import `tempfile` and ask it to make one. Now we download the file into the fresh file.

Now we can begin analyzing the audio. We import `librosa` and read in the audio data using librosa's `load` method, which returns the sample data stored in `y`, and the sample rate stored in `sr`.

We apply two transformations that are very common in audio analysis: we monofy the signal and downsample it to 22050 Hz, because the most salient information tends to lie in the lower bands anyway.

## Calculating Audio Features

Now let's actually calculate the MFCCs. Observe that I made a mistake here, I just told you to downsample and monofy but take the original sample data anyway. Whatever, for demonstration purposes, let's just extract the first 12 MFCCs.

Now using `numpy.mean`, we calculate the average for each MFCC over time using a list comprehension.

## Putting it All Together

Finally, let's write our analysis data into the firestore database. For that we import `uuid` to generate unique IDs, and Google's firestore client, which we initialize with `firestore.Client()`

Let's generate a new `uid` and create a new document in the database, specifying the collection and the `uid` as the document's name. We set some data, namely the blob name, the file name, the length in samples as well as those MFCCs.

Now we can click `Create` and wait a few seconds for Google to set up our function. Let's open the database connection and the bucket in another tab. We upload some test data (note: the audio files need to have a bit depth of 16bit, otherwise it won't work), and after a few seconds our analysis data arrives in the database, voilà.