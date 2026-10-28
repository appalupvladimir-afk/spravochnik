import cv2, numpy as np, sys, json
D=sys.argv[1]
im=cv2.imread(D+'/media/image1.png')
b,g,r=[im[:,:,i].astype(int) for i in range(3)]
redish=((r-g>18)&(r>120)).astype(np.uint8)
redish[:150]=0; redish[:,:1000]=0; redish[875:]=0
dark=((r+g+b)<330).astype(np.uint8)
darkd=cv2.dilate(dark,np.ones((9,9),np.uint8))
cs,_=cv2.findContours(redish,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
pts=np.vstack([c.reshape(-1,2) for c in cs if len(c)>200])
pts=np.array([p for p in pts if not darkd[p[1],p[0]]])
rough={'A':((1292,362),(345,235),35),'B':((1586,276),(260,175),33),'C':((1515,580),(470,330),-25),'D':((1232,733),(335,250),48)}
def edist(p,e):
    (cx,cy),(a,b_),ang=e; t=np.deg2rad(ang)
    x=p[:,0]-cx;y=p[:,1]-cy
    u=x*np.cos(t)+y*np.sin(t); v=-x*np.sin(t)+y*np.cos(t)
    rr=np.sqrt((u/(a/2))**2+(v/(b_/2))**2)
    return (rr-1)*min(a,b_)/2
fits={}
for k,e in rough.items():
    for it in range(6):
        d=np.abs(edist(pts,e))
        sel=pts[d<(30 if it<2 else 8)]
        # drop points inside other rough ellipses (occlusion boundaries)
        e=cv2.fitEllipse(sel.astype(np.float32).reshape(-1,1,2))
    fits[k]=e; print(k,[round(float(x),1) for x in (*e[0],*e[1],e[2])],len(sel))
json.dump({k:[list(map(float,v[0])),list(map(float,v[1])),float(v[2])] for k,v in fits.items()},open(D+'/cell_ellipses.json','w'))
vis=im.copy()
for k,e in fits.items(): cv2.ellipse(vis,e,(255,0,0),2)
cv2.imwrite(D+'/crops/cellfit.png',vis[150:890,1050:])
