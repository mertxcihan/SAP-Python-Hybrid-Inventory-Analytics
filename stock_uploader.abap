REPORT zstok_veri_yukle.

DATA: lt_raw_data TYPE TABLE OF string,
      lv_line     TYPE string.

DATA: BEGIN OF ls_excel,
        urun_kodu TYPE string,
        urun_adi  TYPE string,
        kategori  TYPE string,
        stok      TYPE string,
        depo      TYPE string,
      END OF ls_excel.

DATA: lt_db TYPE TABLE OF zstok_tablo_new,
      ls_db TYPE zstok_tablo_new.

PARAMETERS: p_file TYPE string DEFAULT 'C:\SAP\stok_veri.csv'.

START-OF-SELECTION.

  CALL FUNCTION 'GUI_UPLOAD'
    EXPORTING
      filename = p_file
      filetype = 'ASC'
    TABLES
      data_tab = lt_raw_data
    EXCEPTIONS
      OTHERS   = 1.

  IF sy-subrc <> 0.
    WRITE: / 'Hata: Dosya okunamadi.'.
    EXIT.
  ENDIF.

  DELETE FROM zstok_tablo_new.
  COMMIT WORK.

  LOOP AT lt_raw_data INTO lv_line.
    IF sy-tabix = 1 OR lv_line IS INITIAL OR lv_line CS 'URUN_KODU'.
      CONTINUE.
    ENDIF.

    SPLIT lv_line AT ';' INTO ls_excel-urun_kodu
                              ls_excel-urun_adi
                              ls_excel-kategori
                              ls_excel-stok
                              ls_excel-depo.

    CONDENSE ls_excel-stok NO-GAPS.

    CLEAR ls_db.
    ls_db-mandt      = sy-mandt.
    ls_db-urun_kodu  = ls_excel-urun_kodu.
    ls_db-urun_adi   = ls_excel-urun_adi.
    ls_db-kategori   = ls_excel-kategori.
    ls_db-stok       = ls_excel-stok.
    ls_db-depo       = ls_excel-depo.

    IF ls_db-urun_kodu IS NOT INITIAL.
      APPEND ls_db TO lt_db.
    ENDIF.
  ENDLOOP.

  IF lt_db IS NOT INITIAL.
    MODIFY zstok_tablo_new FROM TABLE lt_db.
    IF sy-subrc = 0.
      COMMIT WORK.
      WRITE: / 'ISLEM DURUMU: BASARILI'.
      WRITE: / 'TOPLAM KAYIT :', sy-dbcnt.
      WRITE: / 'TABLO ADI    :', 'ZSTOK_TABLO_NEW'.
      WRITE: / 'KULLANICI    :', sy-uname.
    ENDIF.
  ENDIF.
  
