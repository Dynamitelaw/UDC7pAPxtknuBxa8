try:
    import keras
    print("\n####################################################")
    print("SUCCESS! Keras has been successfully installed")
    print("####################################################")
except Exception as e:
    print("\n#########################")
    print("ERROR: " + str(e))
    print("#########################")