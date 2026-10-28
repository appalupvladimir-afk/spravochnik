import cv2, numpy as np, sys, json
D,OUT=sys.argv[1],sys.argv[2]
K=lambda n: np.ones((n,n),np.uint8)
def fill_holes(m):
    cs,_=cv2.findContours(m.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    o=np.zeros(m.shape,np.uint8); cv2.drawContours(o,cs,-1,1,-1); return o
def comp_at(mask,pt):
    n,lab=cv2.connectedComponents(mask.astype(np.uint8),connectivity=4)
    return (lab==lab[pt[1],pt[0]]).astype(np.uint8)
meta={}
for step,img in ((1,2),(2,3),(3,4)):
    im=cv2.imread(f'{D}/media/image{img}.png'); H,W=im.shape[:2]
    b,g,r=[im[:,:,j].astype(int) for j in range(3)]
    mx=np.maximum(np.maximum(r,g),b); mn=np.minimum(np.minimum(r,g),b)
    darkn=((mx<150)|((mx-mn<30)&(mx<215))).astype(np.uint8)
    nw=((mn<250)&(darkn==0)).astype(np.uint8)
    if step==1:
        char=comp_at(nw,(200,600)); blob=comp_at(nw,(1000,600))
    elif step==2:
        comp=comp_at(nw,(600,600))
        poly=np.array([[0,0],[1203,0],[1203,300],[1197,440],[1187,468],[1150,560],[1050,700],[1000,H],[0,H]],np.int32)
        left=np.zeros((H,W),np.uint8); cv2.fillPoly(left,[poly],1)
        blob=comp&left; char=comp&(1-left)
        char=comp_at(char,(1400,700))
    else:
        comp=comp_at(nw,(1500,720))
        orange=((g-b)>18)&(r>200)
        chr_like=(comp==1)&~orange
        region=np.zeros((H,W),np.uint8); region[:, :470]=1
        cand=((comp==1)&((region==0)|chr_like)).astype(np.uint8)
        # character = everything left of x=470 that is not orange-blob
        c2=((comp==1)&(region==1)&chr_like).astype(np.uint8)
        c2=cv2.morphologyEx(c2,cv2.MORPH_OPEN,K(3))
        n_,lab_,st_,_=cv2.connectedComponentsWithStats(c2,connectivity=4); char=(lab_==1+np.argmax(st_[1:,4])).astype(np.uint8)
        blob=(comp&(1-cv2.dilate(char,K(3)))).astype(np.uint8)
        bo=cv2.morphologyEx(blob,cv2.MORPH_OPEN,K(5)); n_,lab_,st_,_=cv2.connectedComponentsWithStats(bo,connectivity=4); blob=(lab_==1+np.argmax(st_[1:,4])).astype(np.uint8)
    char=fill_holes(char)
    # blob: include enclosed text/number
    blob_f=fill_holes(cv2.morphologyEx(blob,cv2.MORPH_CLOSE,K(5)))
    blob_f&=(1-char)
    hidden=np.zeros((H,W),np.uint8)
    hull=cv2.convexHull(cv2.findNonZero(blob_f)); hm=np.zeros((H,W),np.uint8); cv2.fillPoly(hm,[hull],1)
    NB={1:(425,115,525,350),2:(95,140,275,370),3:(300,150,600,560)}[step]
    box=np.zeros((H,W),np.uint8); box[NB[1]:NB[3],NB[0]:NB[2]]=1
    hidden=(hm&box&(1-blob_f)).astype(np.uint8)
    blob_f=(blob_f|hidden).astype(np.uint8)
    # ---- blob RGBA (inpaint text, number, hidden area) ----
    fix=((cv2.dilate(darkn,K(5))&blob_f)|cv2.dilate(hidden,K(5))|(cv2.dilate(char,K(13))&blob_f)).astype(np.uint8)
    rec=cv2.inpaint(im,fix*255,7,cv2.INPAINT_TELEA)
    rec=np.where(fix[:,:,None]==1,cv2.GaussianBlur(rec,(0,0),4),rec)
    rec=cv2.inpaint(rec,(fix*0)*255,1,cv2.INPAINT_TELEA)
    a=cv2.GaussianBlur(blob_f.astype(np.float32),(0,0),0.7)
    x,y,w,h=cv2.boundingRect(blob_f); x=max(0,x-2);y=max(0,y-2);w+=4;h+=4
    cv2.imwrite(f'{OUT}/step{step}-blob.png',np.dstack([rec,(a*255).astype(np.uint8)])[y:y+h,x:x+w])
    meta[f'blob{step}']=dict(x=x,y=y,w=w,h=h)
    # ---- character RGBA ----
    inner=cv2.erode(char,K(5))
    band=cv2.dilate(char,K(5))&(1-inner)
    f=im.astype(np.float32)/255
    a_ctw=np.clip((1-f.min(axis=2))/0.16,0,1)        # colour-to-alpha against white
    nearblob=cv2.dilate(blob_f,K(9))
    alpha=np.where(inner==1,1.0,0.0)
    alpha=np.where((band==1)&(nearblob==0),a_ctw,alpha)
    soft=cv2.GaussianBlur(char.astype(np.float32),(0,0),0.8)
    alpha=np.where((band==1)&(nearblob==1),soft,alpha)
    A=np.maximum(alpha,1e-4)[:,:,None]
    col=np.where((band==1)[:,:,None]&(nearblob==0)[:,:,None],(f-(1-A))/A,f)
    col=np.clip(col,0,1)
    x,y,w,h=cv2.boundingRect((alpha>0.01).astype(np.uint8)); x=max(0,x-2);y=max(0,y-2);w+=4;h+=4
    rgba=np.dstack([(col*255).astype(np.uint8),(alpha*255).astype(np.uint8)])[y:y+h,x:x+w]
    cv2.imwrite(f'{OUT}/step{step}-char.png',rgba)
    meta[f'char{step}']=dict(x=x,y=y,w=w,h=h)
    # ---- ellipse outline ----
    thin=(darkn&(1-cv2.dilate(blob_f,K(7)))&(1-cv2.dilate(char,K(7)))).astype(np.uint8)
    thin&=(1-cv2.dilate(cv2.morphologyEx(darkn,cv2.MORPH_OPEN,K(7)),K(9)))
    n,lab,st,_=cv2.connectedComponentsWithStats(thin)
    pts=[]
    for k in range(1,n):
        X,Y,Wc,Hc,Ar=st[k]
        if max(Wc,Hc)>60: pts.append(np.column_stack(np.nonzero(lab==k)[::-1]))
    pts=np.vstack(pts).astype(np.float32)
    e=cv2.fitEllipse(pts.reshape(-1,1,2))
    # line thickness ~ area / length
    meta[f'ellipse{step}']=dict(cx=e[0][0],cy=e[0][1],w=e[1][0],h=e[1][1],angle=e[2],n=int(len(pts)))
    meta[f'size{step}']=dict(w=W,h=H)
    print(step,meta[f'ellipse{step}'],meta[f'blob{step}'],meta[f'char{step}'])
    vis=im.copy(); cv2.ellipse(vis,e,(255,0,255),1); cv2.imwrite(f'{D}/crops/efit{step}.png',vis)
json.dump(meta,open(D+'/steps_meta.json','w'),indent=1)
# ---- front arcs of outline (where the line is drawn over the blob) ----
for step,img in ((1,2),(2,3),(3,4)):
    im=cv2.imread(f'{D}/media/image{img}.png'); H,W=im.shape[:2]
    b,g,r=[im[:,:,j].astype(int) for j in range(3)]
    mx=np.maximum(np.maximum(r,g),b); mn=np.minimum(np.minimum(r,g),b)
    dark=((mx<170)|((mx-mn<30)&(mx<215))).astype(np.uint8)
    blob=cv2.imread(f'{OUT}/step{step}-blob.png',cv2.IMREAD_UNCHANGED); m=meta[f'blob{step}']
    bm=np.zeros((H,W),np.uint8); bm[m['y']:m['y']+m['h'],m['x']:m['x']+m['w']]=(blob[:,:,3]>128)[:H-m['y'],:W-m['x']]
    bm=cv2.erode(bm,K(5)); darkd=cv2.dilate(dark,K(5))
    e=meta[f'ellipse{step}']; cx,cy,a,bb,ang=e['cx'],e['cy'],e['w']/2,e['h']/2,np.deg2rad(e['angle'])
    N=3000; t=np.linspace(0,2*np.pi,N,endpoint=False)
    X=cx+a*np.cos(t)*np.cos(ang)-bb*np.sin(t)*np.sin(ang); Y=cy+a*np.cos(t)*np.sin(ang)+bb*np.sin(t)*np.cos(ang)
    front=np.zeros(N,bool)
    for i in range(N):
        xi,yi=int(round(X[i])),int(round(Y[i]))
        if 0<=xi<W and 0<=yi<H and bm[yi,xi] and darkd[yi,xi]: front[i]=True
    # close small gaps (text crossing etc.), drop tiny runs
    from scipy.ndimage import binary_closing, binary_opening
    front=binary_opening(binary_closing(front,np.ones(25),mode='wrap') if False else binary_closing(np.r_[front,front,front],np.ones(25))[N:2*N],np.ones(15))
    runs=[];i=0
    while i<N:
        if front[i]:
            j=i
            while j<N and front[j]: j+=1
            runs.append((float(t[i]),float(t[j-1]))); i=j
        else: i+=1
    meta[f'front{step}']=runs
    print('front arcs',step,[(round(np.rad2deg(p),1),round(np.rad2deg(q),1)) for p,q in runs])
json.dump(meta,open(D+'/steps_meta.json','w'),indent=1)
