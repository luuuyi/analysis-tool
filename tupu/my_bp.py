import tensorflow as tf   
import numpy as np   
  
def addLayer(inputData,inSize,outSize,layer_name,activity_function = None): 
	with tf.name_scope(layer_name+'layer'):
		Weights = tf.Variable(tf.random_normal([inSize,outSize]),name='w')
		tf.summary.histogram("weights",Weights)  
		basis = tf.Variable(tf.zeros([1,outSize])+0.1,name='b')
		tf.summary.histogram("basis",basis)
		weights_plus_b = tf.matmul(inputData,Weights)+basis 
		if activity_function is None:  
			ans = weights_plus_b  
		else:  
			ans = activity_function(weights_plus_b)  
		return ans  

x_data = np.array([[4, 7],[4, 7], [1, 1]])
y_data = np.array([[1], [2], [3]])

'''x_data = np.array([[0.35, 0.9]])
y_data = np.array([[0.5]])'''

with tf.name_scope('input'): 
	xs = tf.placeholder(tf.float32,[None,2],name='x_input') # 样本数未知，特征数为1，占位符最后要以字典形式在运行中填入  
	ys = tf.placeholder(tf.float32,[None,1],name='y_label')  
  
l1 = addLayer(xs,2,3,'l1',activity_function=tf.nn.sigmoid) # relu是激励函数的一种  
l2 = addLayer(l1,3,3,'l2',activity_function=tf.nn.sigmoid) # relu是激励函数的一种 
l3 = addLayer(l2,3,1,'l3',activity_function=None)  

with tf.name_scope('loss'):
	loss = tf.reduce_mean(tf.reduce_sum(tf.square((ys-l3)),reduction_indices = [1]))#需要向相加索引号，redeuc执行跨纬度操作
tf.summary.scalar('loss',loss)

'''l1 = addLayer(xs,2,2,activity_function=tf.nn.sigmoid) # relu是激励函数的一种   
l2 = addLayer(l1,2,1,activity_function=None)
loss = tf.reduce_mean(tf.reduce_sum(tf.square((ys-l2)),reduction_indices = [1]))#需要向相加索引号，redeuc执行跨纬度操作'''

with tf.name_scope('train'):
	train =  tf.train.GradientDescentOptimizer(0.1).minimize(loss) # 选择梯度下降法  

init = tf.initialize_all_variables()  
sess = tf.Session()
writer = tf.summary.FileWriter('./log/', sess.graph)
merged = tf.summary.merge_all()

params=tf.trainable_variables()
print("Trainable variables:------------------------")
for idx, v in enumerate(params):
	print("  param {:3}: {:15}   {}".format(idx, str(v.get_shape()), v.name))

sess.run(init)
for i in range(1000):  
	sess.run(train,feed_dict={xs:x_data,ys:y_data})
	if i%50 == 0:
		print(sess.run(l3,feed_dict={xs:x_data,ys:y_data}))
		print(sess.run(loss,feed_dict={xs:x_data,ys:y_data}))
		result = sess.run(merged,feed_dict={xs:x_data,ys:y_data})
		writer.add_summary(result,i)

print(sess.run(params))