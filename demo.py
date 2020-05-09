from Library.Spout import Spout
import cv2

def main() :
    spout = Spout(displayMode = 'Receive', displayWindow = True)
    receiver_name = 'py_receiver'
    spout.receiverInit(receiver_name)
    sender_name = 'py_sender'
    spout.senderInit(sender_name)

    while True :
        receive_img = spout.receiverData()
        
        img = cv2.GaussianBlur(receive_img,(3,3),0)
        send_img = cv2.Canny(img, 50, 150)
        send_img = cv2.cvtColor(send_img,cv2.COLOR_GRAY2BGRA)

        spout.senderData(send_img)
        
        cv2.imshow('sender',send_img)

        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()