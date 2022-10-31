from . import visual_perception
from flask import render_template,url_for, request, session,current_app,redirect
import datetime
from .. import db
from ..models import vp_imgs,vp_classification
import pandas as pd
from .forms import imgs_classi,upload_img
from .. import photos
import os
from .ImageTag_extractor import ImageTag_extractor_execution

@visual_perception.route("/vp",methods=['GET','POST'])
def vp():

    return render_template('vp/vp.html',current_time=datetime.datetime.utcnow())

@visual_perception.route("/imgs_classification",methods=['GET','POST'])
def imgs_classification():
    #form=imgs_classi()

    page=request.args.get('page', 1, type=int)
    query=vp_imgs.query
    pagination=query.order_by(vp_imgs.index).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    imgs_info=pagination.items

    vp_classi=vp_classification.query.all()
    #print("_"*50)
    #exist=db.session.query(db.exists().where(vp_classification.index == 0)).scalar()
    #print(exist)

    if request.method == 'GET':
        return render_template('vp/imgs_classification.html', imgs_info=imgs_info,vp_classi=vp_classi,pagination=pagination) #form=form,
    else:
        img_index=request.form.get('img_index')
        img_fp=request.form.get('img_fp')
        classi=int(request.form.get('classi'))
        img_current=vp_classification.query.filter(vp_classification.imgs_fp==img_fp).first()
        classi_dic_value={1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0}
        classi_dic_name={1:u'林荫',2:u'窄建',3:u'窄木',4:u'宽建',5:u'宽木',6:u'阔建',7:u'阔木',8:u'开阔'} #中文一定要加u，即unicode( str_name )，否则服务器段如果是py2.7，会提示错误。
        classi_dic_value.update({classi:1})
        img_classification=classi_dic_name[classi]
        if not img_current:
            img_classi_info=vp_classification(imgs_fp=img_fp,
                                              c_1=classi_dic_value[1],
                                              c_2=classi_dic_value[2],
                                              c_3=classi_dic_value[3],
                                              c_4=classi_dic_value[4],
                                              c_5=classi_dic_value[5],
                                              c_6=classi_dic_value[6],
                                              c_7=classi_dic_value[7],
                                              c_8=classi_dic_value[8],
                                              classification=img_classification,
                                              index=img_index)
            db.session.add(img_classi_info)
            db.session.commit()
        else:
            query_results=[{1:c_1,2:c_2,3:c_3,4:c_4,5:c_5,6:c_6,7:c_7,8:c_8} for c_1,c_2,c_3,c_4,c_5,c_6,c_7,c_8 in db.session.query(vp_classification.c_1,vp_classification.c_2,vp_classification.c_3,vp_classification.c_4,vp_classification.c_5,vp_classification.c_6,vp_classification.c_7,vp_classification.c_8).filter(vp_classification.imgs_fp==img_fp)][0]
            query_results_update=pd.DataFrame.from_dict(query_results,orient='index').add(pd.DataFrame.from_dict(classi_dic_value,orient='index'))
            img_classification_=classi_dic_name[query_results_update.idxmax()[0]]
            query_results_update_dic=query_results_update.squeeze('columns').to_dict()
            query_results_update_dic.update({'classification':img_classification_})
            query_results_update_dic_=dict(zip(['c_1','c_2','c_3','c_4','c_5','c_6','c_7','c_8','classification'],query_results_update_dic.values()))
            vp_classification.query.filter_by(imgs_fp=img_fp).update(query_results_update_dic_)
            db.session.commit()

    return render_template('vp/imgs_classification.html',imgs_info=imgs_info,vp_classi=vp_classi,pagination=pagination) #,form=form ,

@visual_perception.route("/img_prediction",methods=['GET','POST'])
def img_prediction():
    import os
    form=upload_img()
    if form.validate_on_submit():
        img_name=photos.save(form.photo.data)
        img_url=photos.url(img_name)
        img_fp=os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'],img_name)
        imgs_pred_tag=ImageTag_extractor_execution(img_fp).execution()
        return render_template('vp/img_prediction.html', form=form, img_url=img_url, imgs_pred_tag=imgs_pred_tag)
    else:
        img_url=None
        return render_template('vp/img_prediction.html', form=form, img_url=img_url)

