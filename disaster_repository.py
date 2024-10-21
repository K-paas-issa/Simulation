from dbutils import engineconn
from db_models import DisasterNotification
from sqlalchemy.orm import Session

engine_conn = engineconn()

def save(data: DisasterNotification):
    print('save start')
    session: Session = engine_conn.get_session()

    try:
        # 데이터베이스에 추가하고 커밋
        session.add(data)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving to database: {e}")
    finally:
        print('save data end')
        session.close()

def existBySn(serial_number):
    session: Session = engine_conn.get_session()
    isExist = session.query(DisasterNotification).filter(DisasterNotification.sn == serial_number).count() > 0
    session.close()
    return isExist