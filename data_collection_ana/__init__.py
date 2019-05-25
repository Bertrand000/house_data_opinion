import numpy as np

def func02(kjz1,k):    #k个均值分k份

    kjz1=np.sort(kjz1);#正序
    wb2=kjz1.copy();
    #初始均匀分组wb1
    xlb=[];a=round(len(wb2)/(k));b=len(wb2)%(k);
    for j in range(1,k+1):
        xlb.append(j*a)
        if j==k:
            xlb[j-1]=xlb[j-1]+b;
    j=0;wb1=[];
    for j in range(0,k):
        wb1.append([])
    i=0;j=0;
    while(i<=len(wb2)-1):
        wb1[j].append(wb2[i]);
        if i>=xlb[j]-1:
            j=j+1;
        i=i+1;
    kj1=means(wb1);#初始分组均值

    bj=1;
    while(True):
        wb2=kjz1.copy().tolist();
        if bj!=1:
            kj1=kj2.copy();

        wb3=[];
        for j in range(0,k-1):
            wb3.append([])
        for j in range(0,k-1):
            i=-1;
            while(True):
                if wb2[i]<=kj1[j]:
                    wb3[j].append(wb2.pop(i));
                else:
                    i=i+1;
                if i>=len(wb2):
                    break
        wb3.append(wb2)

        kj2=means(wb3);#过程均值
        if bj==2:
            if kj1==kj2:
                break
        bj=2;
    return wb3

def means(lb1):    #计算均值

    mean1=[];mean2=[];std1=[];
    for j in lb1:
        mean1.append(np.mean(j).tolist())
    for j in range(1,len(mean1)):
        mean2.append(np.mean([mean1[j-1],mean1[j]])) #分组均值使用各组的均值
    print(mean2)
    return mean2

if __name__=='__main__':


    kjz1={"特朗普":0,"新房":0,"拆迁":0,"流量":1,"万科":89,"房屋出租":101}   #生成随机数列表
    keys = list(kjz1.keys())
    values = list(kjz1.values())
    # 默认k=3
    k=3
    kjz3=func02(values,k)    #k个均值分k份
    for index,j in enumerate(kjz3):
        for indexv,i in enumerate(j):
            local_index = values.index(i)
            values.pop(local_index)
            kjz3[index][indexv] = {keys.pop(local_index):i}
    print(kjz3)
