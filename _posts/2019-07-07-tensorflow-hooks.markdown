---
layout: post
title:  "Hooks in tensorflow"
date:   2019-07-07
categories: tensorflow
author: moontree
---

# Tensorflow Hooks

所有的hook都来源于一个基类，`SessionRunHook`，以观察者模式运行，可以在以下四个时间点被通知：
 -  when a session starts being used
 - before a call to the `session.run()`
 - after a call to the `session.run()`
 - when the session closed


## 代码

```
class ExampleHook(SessionRunHook):
    def begin(self):
      # You can add ops to the graph here.
      print('Starting the session.')
      self.your_tensor = ...

    def after_create_session(self, session, coord):
      # When this is called, the graph is finalized and
      # ops can no longer be added to the graph.
      print('Session created.')

    def before_run(self, run_context):
      print('Before calling session.run().')
      return SessionRunArgs(self.your_tensor)

    def after_run(self, run_context, run_values):
      print('Done running one step. The value of my tensor: %s',
            run_values.results)
      if you-need-to-stop-loop:
        run_context.request_stop()

    def end(self, session):
      print('Done with the session.')
```

### 预定义好的hooks
 - StopAtStepHook: Request stop based on global_step
 - CheckpointSaverHook: saves checkpoint
 - LoggingTensorHook: outputs one or more tensor values to log
 - NanTensorHook: Request stop if given `Tensor` contains Nans.
 - SummarySaverHook: saves summaries to a summary writer


## 更好的理解
```
with MonitoredTrainingSession(hooks=your_hooks, ...) as sess:
    while not sess.should_stop():
      sess.run(your_fetches)
```
上述代码的实际执行流程如下
```
call hooks.begin()
sess = tf.Session()
call hooks.after_create_session()
while not stop is requested:
    call hooks.before_run()
    try:
        results = sess.run(merged_fetches, feed_dict=merged_feeds)
    except (errors.OutOfRangeError, StopIteration):
        break
    call hooks.after_run()
call hooks.end()
sess.close()
```

从上述流程可以看出，
hook.begin()提供了增加ops的功能；
而`hook.before_run()`中需要设置hook要观察的TensorFlow，也可以通过feed_dict来给placeholder赋值数赋值；
`hook.after_run()`可以根据得到的结果，取出对应的值并进行相应处理

### 一个自定义hook的例子
```
class _LearningRateSetterHook(tf.train.SessionRunHook):
    """Sets learning_rate based on global step."""

    def begin(self):
        self._global_step_tensor = tf.train.get_or_create_global_step()
        self._lrn_rate_tensor = tf.get_default_graph().get_tensor_by_name('learning_rate:0') # 注意，这里根据name来索引tensor，所以请在定义学习速率的时候，为op添加名字
        self._lrn_rate = 0.1 # 第一阶段的学习速率

    def before_run(self, run_context):
        return tf.train.SessionRunArgs(
            self._global_step_tensor,  # Asks for global step value.
            feed_dict={self._lrn_rate_tensor: self._lrn_rate}
        )  # Sets learning rate

    def after_run(self, run_context, run_values):
        train_step = run_values.results
        if train_step < 10000:
            pass
        elif train_step < 20000:
            self._lrn_rate = 0.01 # 第二阶段的学习速率
        elif train_step < 30000:
            self._lrn_rate = 0.001 # 第三阶段的学习速率
        else:
            self._lrn_rate = 0.0001 # 第四阶段的学习速率

```


## 需要注意的地方
由于hook机制和MonitoredTrainingSession进行了绑定，部分情况下使用hook会带来不好的体验。

每次执行`sess.run()`,所有`hook`的内容都会被执行一次。

当然了，一般情况下不会有这个问题，但是，当需要通过`sess.run()`来获取数据，并且把数据的值作为`feed_dict`的值传递给另一个`placeholder`时，使用hook就会导致错误。
例子代码如下：
```
train_image, train_label = get_batch()
eval_image, eval_label = get_batch()
images = tf.placeholder()
labels = tf.placeholder()

with MonitoredTrainingSession(hooks=your_hooks, ...) as sess:
    while not sess.should_stop():
      _image, _label = sess.run([train_image, train_label])
      _ = sess.run(train_op, feed_dict={images: _image, labels: _label})
```

由于每次都要执行`hook`的内容，而用来获取数据的`run`并未对应`loss`等`feteches`，会导致程序报错。

### 源码分析，
`hooks`和`MonitoredTrainingSession()`的依赖关系以及观察者模式的实现，部分源码如下：
可以发现，并未提供某次`sess.run()`时只执行部分`hook`的操作。

```
class MonitoredTrainingSession():
    def __init__():
        # ...
        return MonitoredSession(
            session_creator=session_creator,
            hooks=all_hooks,
            stop_grace_period_secs=stop_grace_period_secs
        )

class MonitoredSession(_MonitoredSession):
    def __init__(self, session_creator=None, hooks=None,
           stop_grace_period_secs=120):
        super(MonitoredSession, self).__init__(
            session_creator, hooks, should_recover=True,
            stop_grace_period_secs=stop_grace_period_secs
        )

class _MonitoredSession(object):
    def __init__(self, session_creator, hooks, should_recover,
           stop_grace_period_secs=120):
        self._graph_was_finalized = ops.get_default_graph().finalized
        self._hooks = hooks or []
        for h in self._hooks:
            h.begin()
        # ...
        self._coordinated_creator = self._CoordinatedSessionCreator()
        self._sess = self._coordinated_creator.create_session()

    def run(self, fetches, feed_dict=None, options=None, run_metadata=None):

        return self._sess.run(
            fetches,
            feed_dict=feed_dict,
            options=options,
            run_metadata=run_metadata
        )

    class _CoordinatedSessionCreator(SessionCreator):
        """Factory for the _RecoverableSession."""

        def __init__(self, session_creator, hooks, stop_grace_period_secs):
            self._session_creator = session_creator
            self._hooks = hooks
            self.coord = None
            self.tf_sess = None
            self._stop_grace_period_secs = stop_grace_period_secs

        def create_session(self):
            """Creates a coordinated session."""
            # Keep the tf_sess for unit testing.
            self.tf_sess = self._session_creator.create_session()
            # We don't want coordinator to suppress any exception.
            self.coord = coordinator.Coordinator(clean_stop_exception_types=[])
            if ops.get_collection(ops.GraphKeys.QUEUE_RUNNERS):
            queue_runner.start_queue_runners(sess=self.tf_sess, coord=self.coord)
            # Inform the hooks that a new session has been created.
            for hook in self._hooks:
                hook.after_create_session(self.tf_sess, self.coord)
            return _CoordinatedSession(
                _HookedSession(self.tf_sess, self._hooks), self.coord,
                self._stop_grace_period_secs)


class _HookedSession(_WrappedSession):
    def __init__(self, sess, hooks):
        _WrappedSession.__init__(self, sess)
        self._hooks = hooks

    def run(self, fetches, feed_dict=None, options=None, run_metadata=None):
        # do something
        actual_fetches = {'caller': fetches}

        run_context = session_run_hook.SessionRunContext(
            original_args=session_run_hook.SessionRunArgs(fetches, feed_dict),
            session=self._sess
        )
        feed_dict = self._call_hook_before_run(run_context, actual_fetches,
                                           feed_dict, options)
        for hook in self._hooks:
            hook.after_run(
                run_context,
                session_run_hook.SessionRunValues(
                    results=outputs[hook] if hook in outputs else None,
                    options=options,
                    run_metadata=run_metadata
                )
            )

    def _call_hook_before_run(self, run_context, fetch_dict, user_feed_dict,
                            options):
        """Calls hooks.before_run and handles requests from hooks."""
        hook_feeds = {}
        for hook in self._hooks:
            request = hook.before_run(run_context)
            if request is not None:
                if request.fetches is not None:
                    fetch_dict[hook] = request.fetches
            if request.feed_dict:
                self._raise_if_feeds_intersects(
                    hook_feeds, request.feed_dict,
                    'Same tensor is fed by two hooks.')
                hook_feeds.update(request.feed_dict)
            if request.options:
                self._merge_run_options(options, request.options)

        if not hook_feeds:
            return user_feed_dict

        if not user_feed_dict:
            return hook_feeds

        self._raise_if_feeds_intersects(
            user_feed_dict, hook_feeds,
            'Same tensor is fed by a SessionRunHook and user.')
        hook_feeds.update(user_feed_dict)
        return hook_feeds

```




## 无奈之下的替代方案
其实仔细分析hook的机制，会发现，它只是隐藏了部分处理的细节，使得训练代码不再臃肿。
参照执行流程部分，其实可以不采用hook机制，而是在构建graph的时候，将需要观测的`tensor`都记录到一个`dict`中，
每次执行`sess.run`的时候去作为`fetches`之一，然后进行后处理。
后处理部分可以封装成对应的函数`postprocess(values)`来使代码变得整洁。