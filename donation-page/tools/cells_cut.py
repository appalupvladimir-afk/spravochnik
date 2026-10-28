import cv2, numpy as np, sys, json
D,OUT=sys.argv[1],sys.argv[2]
im=cv2.imread(D+'/media/image1.png'); H,W=im.shape[:2]
b,g,r=[im[:,:,i].astype(int) for i in range(3)]
E=json.load(open(D+'/cell_ellipses.json'))
def emask(k,grow=0):
    (cx,cy),(a,bb),ang=E[k]; m=np.zeros((H,W),np.uint8)
    cv2.ellipse(m,((cx,cy),(a+grow,bb+grow),ang),1,-1); return m
mx=np.maximum(np.maximum(r,g),b); dark=((mx<120)|((mx-np.minimum(np.minimum(r,g),b)<40)&(mx<200))).astype(np.uint8)
darkd=cv2.dilate(dark,np.ones((7,7),np.uint8))
notwhite=(np.minimum(np.minimum(b,g),r)<250).astype(np.uint8)
order=['A','B','D','C']   # back → front
front_of={'A':['C'],'D':['C'],'B':[],'C':[]}
meta={}
for k in order:
    e=emask(k,4)
    vis=e&notwhite
    vis=cv2.morphologyEx(vis,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    occl=np.zeros_like(e)
    for f in front_of[k]: occl|=emask(f,6)&emask(k,-2)
    alpha=(vis|occl).astype(np.uint8)
    alpha&=(1-(cv2.dilate(dark,np.ones((5,5),np.uint8))&(1-emask(k,-10)))).astype(np.uint8)
    # fill holes
    ff=alpha.copy(); cnts,_=cv2.findContours(ff,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    alpha=np.zeros_like(ff); cv2.drawContours(alpha,cnts,-1,1,-1); alpha&=emask(k,4)
    whiteish=(np.minimum(np.minimum(b,g),r)>244).astype(np.uint8)
    edge=(1-emask(k,-24)).astype(np.uint8)
    neartext=cv2.dilate(dark,np.ones((31,31),np.uint8))
    alpha&=(1-(whiteish&edge&neartext)).astype(np.uint8)
    alpha&=(1-(cv2.dilate(dark,np.ones((5,5),np.uint8))&edge)).astype(np.uint8)
    alpha=cv2.morphologyEx(alpha,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    # pixels to reconstruct: text/line inside, and occluded zone
    fix=((darkd&emask(k,4))|occl).astype(np.uint8)
    # don't use other cells' pixels in the occluded area as source: inpaint them
    src=im.copy()
    rec=cv2.inpaint(src,fix*255,9,cv2.INPAINT_TELEA)
    # second smoothing pass inside fix
    blur=cv2.GaussianBlur(rec,(0,0),3)
    fixs=cv2.GaussianBlur(fix.astype(np.float32),(0,0),2)[:,:,None]
    rec=(rec*(1-fixs*0.6)+blur*(fixs*0.6)).astype(np.uint8)
    a=cv2.GaussianBlur(alpha.astype(np.float32),(0,0),0.9)
    x,y,w,h=cv2.boundingRect(alpha); x-=3;y-=3;w+=6;h+=6
    rgba=np.dstack([rec,(a*255).astype(np.uint8)])[y:y+h,x:x+w]
    cv2.imwrite(f'{OUT}/cell-{k}.png',rgba)
    meta[k]={'x':x,'y':y,'w':w,'h':h}
    print(k,meta[k])
json.dump(meta,open(D+'/cells_meta.json','w'))
