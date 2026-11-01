# Word渲染环境预检

2026-11-02 00:53 Asia/Shanghai。主控使用正式workspace依赖载入，确认捆绑Python/Node路径。普通PowerShell命令实际建立独立隐藏Word.Application，读取Version=16.0后在finally正常Quit，退出0，约4.56秒；未打开用户文档、未改ExecutionPolicy、未kill任何进程。

旧020角色5R007的native OMML builder与math_omml.py为已使用路径，可检查后在本轮作者目录新建适配，不能覆盖旧稿。旧render_with_word.py含-ExecutionPolicy Bypass，本轮禁止原样运行；若canonical render_docx实际缺LibreOffice，保存失败日志后以普通powershell -NoProfile -Command执行受控脚本块，读取自建DOCX导PDF，再由捆绑PDFium渲染并逐页实际看图。只关闭自建Word.Document和Word.Application；不终止用户Word。

第一次正式DOCX authoring前成功运行marker一次，输出数1；现时尚未运行本轮marker、尚未创建本轮Word。所有渲染中间件仅当前角色local-cache。最终所有页必须实际查看，保留内容数量/公式/表格/图、来源匹配和实际QA记录。若有修订须重新渲染最终字节；不能以旧版QA代替。
