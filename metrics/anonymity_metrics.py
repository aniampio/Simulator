import math
import numpy as np
from scipy import stats

def getEntropy(data, num_target_packets):
	columnsNames = ['Entropy'+str(x) for x in range(num_target_packets)]
	entropies = []
	for column in columnsNames:
		dist = data.iloc[0][column]
		# suma = sum([float(x) for x in dist])
		# print("For column %s the sum is %f" % (column, suma))
		# entropies.append()
		entropies.append(dist)
	return np.mean(entropies)


def getUnlinkability(data):
	epsilon = []
	dlts = 0
	est_senderA = data["PrSenderA"]
	est_senderB = data["PrSenderB"]
	est_others = data["PrOthers"]
	realSenderLabel = data["RealSenderLabel"]
	for i, (prA, prB, prO) in enumerate(zip(est_senderA, est_senderB, est_others)):
		suma = float(prA) + float(prB) + float(prO)
		if not math.isclose(suma, 1.0, rel_tol=1e-10):
			print(">>> The probabilities do not sum up to one! Row: %d Sum: %f" % (i, prA + prB + prO))

	for (prA, prB, label) in zip(est_senderA, est_senderB, realSenderLabel):
		# print("PrA %f, PrB %f" % (prA, prB))
		if label == 1:
			if not float(prB) == 0.0:
				ratio = float(prA) / float(prB)
				if not ratio == 0.0:
					lratio = math.log(ratio)
					# print("Lratio %f, Ratio: %f " % (lratio, ratio))
					epsilon.append(lratio)
			else:
				dlts += 1
		elif label == 2:
			if not float(prA) == 0.0:
				ratio = float(prB) / float(prA)
				if not ratio == 0.0:
					lratio = math.log(ratio)
					# print("Lratio %f, Ratio: %f " % (lratio, ratio))
					epsilon.append(lratio)
			else:
				dlts += 1
		else:
			pass

	meanEps = np.mean(epsilon) if epsilon != [] else None
	stdEps = np.std(epsilon) if epsilon != [] else None
	delta = float(dlts) / float(len(est_senderA))

	return (meanEps, stdEps, delta)
