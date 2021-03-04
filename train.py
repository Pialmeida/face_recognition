import G6_iris_recognition as G6

def train():
	train_database_path = r'Input_Database/'
	train_encoding_model_path = r'encodingModel/irisEncodings.pickle'

	G6.iris_model_train(train_database_path,train_encoding_model_path)

def test(filename = None):
	test_encoding_model_path = r'encodingModel/irisEncodings.pickle'
	name = G6.iris_model_test(test_encoding_model_path,r'Input_Database/Pedro Almeida/Pedro Almeida_0.jpg')

	print(f'Name is {name}')

if __name__ == '__main__':
	test()
