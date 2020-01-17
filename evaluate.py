import time
from collections import Counter
import pickle

from models.HMM import HMM
from models.HMM_t1 import HMM1
from models.CRF import CRFModel
from evaluating import Metrics
from operate_bilstm import BiLSTM_operator

from utils import save_model

def hmm_train_eval(train_data,test_data,word2id,tag2id,remove_0=False):
    """hmm模型的评估与训练"""
    print("hmm模型的评估与训练...")
    train_word_lists,train_tag_lists = train_data
    test_word_lists,test_tag_lists = test_data
    hmm_model = HMM(len(tag2id),len(word2id))
    hmm_model.train(train_word_lists,train_tag_lists,word2id,tag2id)

    save_model(hmm_model,"./ckpts/hmm.pkl")

    # 模型评估
    pred_tag_lists = hmm_model.test(test_word_lists,word2id,tag2id)
    metrics = Metrics(test_tag_lists,pred_tag_lists)
    metrics.report_scores()

    return pred_tag_lists

def crf_train_eval(train_data,test_data,remove_0=False):
    """crf模型的评估与训练"""
    print("crf模型的评估与训练...")
    train_word_lists,train_tag_lists = train_data
    test_word_lists,test_tag_lists = test_data
    crf_model = CRFModel()
    crf_model.train(train_word_lists,train_tag_lists)
    save_model(crf_model,"./ckpts/crf.pkl")

    pred_tag_lists = crf_model.test(test_word_lists)

    metrics = Metrics(test_tag_lists,pred_tag_lists)
    metrics.report_scores()

    return pred_tag_lists

def bilstm_train_and_eval(train_data,dev_data,test_data,word2id,tag2id,crf=True,remove_0=False):
    """bilstm模型的评估与训练..."""
    if crf:
        print("bilstm+crf模型的评估与训练...")
    else:
        print("bilstm模型的评估与训练...")

    train_word_lists, train_tag_lists = train_data
    dev_word_lists, dev_tag_lists = dev_data
    test_word_lists, test_tag_lists = test_data

    start = time.time()
    vocab_size = len(word2id)
    out_size = len(tag2id)

    bilstm_operator = BiLSTM_operator(vocab_size,out_size,crf=crf)
    # with open('./ckpts/bilstm.pkl','rb') as fout:
    #     bilstm_operator = pickle.load(fout)
    model_name = "bilstm_crf" if crf else "bilstm"
    print("start to train the {} ...".format(model_name))
    bilstm_operator.train(train_word_lists,train_tag_lists,dev_word_lists,dev_tag_lists,word2id,tag2id)
    save_model(bilstm_operator, "./ckpts/" + model_name + ".pkl")

    print("训练完毕,共用时{}秒.".format(int(time.time() - start)))
    print("评估{}模型中...".format(model_name))
    pred_tag_lists, test_tag_lists = bilstm_operator.test(
        test_word_lists, test_tag_lists, word2id, tag2id)

    metrics = Metrics(test_tag_lists, pred_tag_lists, remove_0=remove_0)
    metrics.report_scores()

    return pred_tag_lists
