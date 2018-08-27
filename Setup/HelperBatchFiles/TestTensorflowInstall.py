try:
    import tensorflow as tf
    hello = tf.constant('Hello, TensorFlow!')
    sess = tf.Session()
    print(sess.run(hello))
    print("\n####################################################")
    print("SUCCESS! Tensorflow has been successfully installed")
    print("####################################################")
except Exception as e:
    print("\n#########################")
    print("ERROR: " + str(e))
    print("#########################")