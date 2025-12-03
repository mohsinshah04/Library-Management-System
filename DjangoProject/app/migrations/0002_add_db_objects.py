# app/migrations/0002_add_db_objects.py
from django.db import migrations

class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE VIEW `mydb`.`v_overdue_loans` AS
            SELECT l.loan_id, u.username, b.title, l.due_date
            FROM `mydb`.`Loans` l
            JOIN `mydb`.`Users` u ON l.user_id = u.user_id
            JOIN `mydb`.`Books` b ON l.book_id = b.book_id
            WHERE l.return_date IS NULL AND l.due_date < CURDATE();
            """,
            reverse_sql="DROP VIEW IF EXISTS `mydb`.`v_overdue_loans`;"
        ),
        migrations.RunSQL(
            sql="""
            DROP TRIGGER IF EXISTS `mydb`.`trg_overdue_notification`;
            CREATE TRIGGER `mydb`.`trg_overdue_notification`
            AFTER UPDATE ON `mydb`.`Loans`
            FOR EACH ROW
            BEGIN
                IF NEW.return_date IS NULL AND NEW.due_date < CURDATE() THEN
                    INSERT INTO `mydb`.`Notifications` (user_id, message, notification_type)
                    VALUES (NEW.user_id, CONCAT('Loan ', NEW.loan_id, ' is overdue!'), 'overdue');
                END IF;
            END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS `mydb`.`trg_overdue_notification`;"
        ),
        migrations.RunSQL(
            sql="""
            DROP PROCEDURE IF EXISTS `mydb`.`sp_user_loans`;
            CREATE PROCEDURE `mydb`.`sp_user_loans` (IN uid INT)
            BEGIN
                SELECT b.title, l.loan_date, l.due_date, l.return_date
                FROM `mydb`.`Loans` l
                JOIN `mydb`.`Books` b ON l.book_id = b.book_id
                WHERE l.user_id = uid;
            END;
            """,
            reverse_sql="DROP PROCEDURE IF EXISTS `mydb`.`sp_user_loans`;"
        ),
        migrations.RunSQL(
            sql="""
            DROP PROCEDURE IF EXISTS `mydb`.`sp_process_overdue`;
            CREATE PROCEDURE `mydb`.`sp_process_overdue` ()
            BEGIN
                DECLARE done INT DEFAULT FALSE;
                DECLARE loanId INT;
                DECLARE cur CURSOR FOR
                    SELECT loan_id FROM `mydb`.`Loans` WHERE return_date IS NULL AND due_date < CURDATE();
                DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

                OPEN cur;
                read_loop: LOOP
                    FETCH cur INTO loanId;
                    IF done THEN
                        LEAVE read_loop;
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM `mydb`.`Fines` WHERE loan_id = loanId) THEN
                        INSERT INTO `mydb`.`Fines` (user_id, loan_id, amount)
                        SELECT user_id, loan_id, 5.00 FROM `mydb`.`Loans` WHERE loan_id = loanId;
                    END IF;
                END LOOP;
                CLOSE cur;
            END;
            """,
            reverse_sql="DROP PROCEDURE IF EXISTS `mydb`.`sp_process_overdue`;"
        ),
    ]
