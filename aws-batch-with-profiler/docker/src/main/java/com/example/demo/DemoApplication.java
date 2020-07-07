package com.example.demo;

import java.nio.ByteBuffer;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.logging.*;

import com.amazonaws.services.codeguruprofiler.AmazonCodeGuruProfilerClientBuilder;
import com.amazonaws.services.codeguruprofiler.model.DescribeProfilingGroupRequest;
import com.amazonaws.services.lambda.AWSLambdaAsync;
import com.amazonaws.services.lambda.AWSLambdaAsyncClientBuilder;
import com.amazonaws.services.lambda.model.InvokeRequest;
import com.amazonaws.services.lambda.model.InvokeResult;
import software.amazon.codeguruprofilerjavaagent.Profiler;

public class DemoApplication {
	private static Profiler profiler;
	private static final String functionName = "StepFuncBatchWithProfiler-dev-async";
	private static final String profilingGroupName = "demoApplication";

	public static void main(String[] args) {
		startProfiler();
		logger().info("Started");
		LinkedList<Future> futureList = new LinkedList<>();
		LinkedList<Future> completedList = new LinkedList<>();
		logger().info("Starting lambdas");
		for (int i = 0; i < 1000; i++) {
			logger().info(String.format("Invoking Lambda %s", i));
			AWSLambdaAsync lambda = AWSLambdaAsyncClientBuilder.defaultClient();
			InvokeRequest invokeRequest = new InvokeRequest()
					.withFunctionName(functionName)
					.withPayload("{}");
			Future<InvokeResult> future_res = lambda.invokeAsync(invokeRequest);
			futureList.add(future_res);
			completedList.add(future_res);
		}
		logger().info("Finished starting lambdas");
		Iterator<Future> futureIter = futureList.iterator();
		logger().info("Waiting for lambdas");
		while (futureIter.hasNext()) {
			System.out.print(".");
			try {
				futureIter.next().get();
			} catch (InterruptedException e) {
				e.printStackTrace();
			} catch (ExecutionException e) {
				e.printStackTrace();
			}
			futureIter.remove();
		}
		logger().info("Lambdas completed");
		for (int i = 0; i < 1000; i++) {
			try {
				logger().info(String.format("Gathering future from Lambda %s", i));
				Future<InvokeResult> futureRes = completedList.get(i);
				InvokeResult res = futureRes.get();
				if (res.getStatusCode() == 200) {
					ByteBuffer response_payload = res.getPayload();
				} else {
					System.out.format("Received a non-OK response from AWS: %d\n",
							res.getStatusCode());
				}
			} catch (InterruptedException e) {
				e.printStackTrace();
			} catch (ExecutionException e) {
				e.printStackTrace();
			}
		}
		logger().info("Finished");
		stopProfiler();
		System.exit(0);
	}

	static Logger logger() {
		Logger logger = Logger.getLogger(DemoApplication.class.getName());
		logger.setLevel(Level.INFO);
		return logger;
	}

	private static void startProfiler() {
		AmazonCodeGuruProfilerClientBuilder.defaultClient().describeProfilingGroup(new DescribeProfilingGroupRequest().withProfilingGroupName(profilingGroupName));
		profiler = new Profiler
				.Builder()
				.profilingGroupName(profilingGroupName)
				.build();
		profiler.start();
	}

	private static void stopProfiler() {
		profiler.stop();
	}

}
