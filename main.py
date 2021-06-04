import sys
import cgns
import flow

#--------------------------------------------------
# main 関数
#--------------------------------------------------
def main(fname0):

    ier = 0

    # 計算ケースセット
    case = cgns.cgns(fname0)

    # 流況
    flw = flow.flow(case)

    #　時間ループ
    for it in range(case.istart, case.iend):

        #現在時刻            
        ctime = case.dt*it
        
        if it % case.iout == 0:
            print('time:{:.1f} [min], Qup:{:.3f}[m3/s]'
                .format(ctime/60., case.get_upstream_q(ctime)))
            # 出力タイミングで出力
            case.write_calc_result(ctime, flw)
        
        # 流況を更新
        ier = flw.update()

    return ier

    # 計算条件を閉じる
    ier = case.close()
    
    return ier

if __name__ == '__main__':
    import time

    #現在のパス設定
    print(sys.path)

    #追加する場合
    # p = ""
    # print(sys.path.append(p))

    if len(sys.argv) == 2:
        start_time = time.time()
        print('> Program starts.')
        if main(sys.argv[1]) == 0:
            process_time = time.time() - start_time
            print('> It took {:.1f} [sec] for this calculation.'.format(process_time)) #2桁まで表示
            # print("It took {}[sec] for this calculation.", process_time)
            print('> Program ended normaly.')
        else:
            print('>>Error : Something\'s wrong.')
    else:
        print('>>Error : Specify the CGNS file as the arguments.')

