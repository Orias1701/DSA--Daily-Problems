// Các thư viện chuẩn của C++ được sử dụng trong chương trình
#include <iostream>  // Dùng cho các luồng nhập/xuất chuẩn (cin, cout, cerr)
#include <fstream>   // Dùng để thao tác đọc/ghi tệp tin (ifstream, ofstream)
#include <sstream>   // Dùng để thao tác với chuỗi như một luồng dữ liệu (stringstream)
#include <iomanip>   // Dùng để định dạng luồng xuất (setfill, setw, hex)
#include <vector>    // Dùng cấu trúc dữ liệu mảng động (vector) để làm bộ đệm
#include <cstdint>   // Dùng cho các kiểu số nguyên có kích thước cố định (uint64_t, uint8_t)
#include <cstring>   // Dùng cho các hàm thao tác bộ nhớ mức thấp như std::memcpy
#include <filesystem>

using namespace std; // Sử dụng không gian tên chuẩn std để không phải viết std:: trước mỗi hàm
namespace fs = std::filesystem;

// Định nghĩa các bí danh (alias) cho kiểu dữ liệu để viết code ngắn gọn hơn
using u64 = uint64_t; // Số nguyên không dấu 64-bit (8 bytes)
using u08 = uint8_t;  // Số nguyên không dấu 8-bit (1 byte)

// Các hằng số thuật toán dùng cho quá trình băm (hashing)
const u64 DEFAULT = 0xcbf29ce484222325ULL; // Giá trị băm khởi tạo ban đầu (seed/offset basis)
const u64 PRIME = 0x100000001b3ULL;        // Số nguyên tố 64-bit dùng để nhân và khuếch tán dữ liệu (FNV prime)
const int SMALL = 13;                      // Số lượng bit sẽ được dịch vòng

/*
 * Hàm bitRotating: Dùng để xoay vòng các bit của một số 64-bit sang trái 'shift' vị trí.
 * Xoay vòng nghĩa là các bit bị đẩy ra khỏi mép trái sẽ được vòng lại chèn vào mép phải.
 */
inline u64 bitRotating(u64 value, int shift)
{
    shift &= 63; // Đảm bảo số lượng bit dịch không vượt quá 63 (tương đương shift % 64)
    if (shift == 0)
        return value; // Nếu không cần dịch thì trả về giá trị nguyên bản
    // Dịch trái 'shift' bit, HOẶC (BITWISE OR) với phần dịch phải (64 - shift) bit để tạo hiệu ứng xoay vòng
    return (value << shift) | (value >> (64 - shift));
}

/*
 * Hàm hashingSuperFast: Đọc dữ liệu từ luồng (stream) và tính toán ra mã băm 64-bit.
 * Thêm các biến tham chiếu (&) để đẩy dữ liệu thống kê ra ngoài hàm main.
 */
u64 hashingSuperFast(istream &stream, u64 &out_total_bytes, u64 &out_total_blocks, u64 &out_read_count)
{
    u64 hash_val = DEFAULT; // Bắt đầu với giá trị băm mặc định
    
    // Khởi tạo các biến thống kê về 0
    out_total_bytes = 0;
    out_total_blocks = 0;
    out_read_count = 0;

    // Đảm bảo kích thước buffer (bộ đệm) chia hết cho 8 để tối ưu đọc khối 64-bit
    constexpr streamsize BUFFER_SIZE = 8192; // Kích thước bộ đệm là 8KB
    vector<char> buffer(BUFFER_SIZE);        // Tạo bộ đệm trong RAM bằng vector

    // Vòng lặp đọc tệp liên tục cho đến khi kết thúc luồng dữ liệu (EOF)
    while (stream)
    {
        // Đọc tối đa BUFFER_SIZE byte từ luồng vào bộ đệm
        stream.read(buffer.data(), BUFFER_SIZE);
        streamsize bytes_read = stream.gcount(); // Lấy số byte THỰC TẾ vừa đọc được
        if (bytes_read == 0) break;              // Nếu không đọc được byte nào -> Thoát vòng lặp

        out_read_count++; // Tăng biến đếm số lần load dữ liệu vào RAM
        out_total_bytes += static_cast<u64>(bytes_read); // Cộng dồn vào tổng số byte/kí tự của tệp

        // Tính toán số lượng khối 64-bit (8 bytes) có thể xử lý trong lần đọc này
        streamsize blocks = bytes_read / 8;
        streamsize remainder = bytes_read % 8; // Số byte lẻ còn lại ở cuối chưa đủ tạo thành khối 8 byte

        out_total_blocks += static_cast<u64>(blocks); // Cộng dồn tổng số khối 64-bit đã xử lý

        // Ép kiểu mảng char thành mảng các byte không dấu (u08) để xử lý dữ liệu nhị phân chuẩn xác
        const u08 *data = reinterpret_cast<const u08 *>(buffer.data());

        // 1. XỬ LÝ KHỐI 64-BIT (Tối ưu tốc độ: Xử lý 8 byte cùng một lúc)
        for (streamsize i = 0; i < blocks; ++i)
        {
            u64 block64;
            std::memcpy(&block64, data + (i * 8), sizeof(u64));

            hash_val ^= block64;                     
            hash_val *= PRIME;                       
            hash_val = bitRotating(hash_val, SMALL); 
        }

        // 2. XỬ LÝ PHẦN DƯ (Tail Processing)
        streamsize offset = blocks * 8; // Vị trí bắt đầu của các byte lẻ
        for (streamsize i = 0; i < remainder; ++i)
        {
            hash_val ^= static_cast<u08>(data[offset + i]); 
            hash_val *= PRIME;                              
            hash_val = bitRotating(hash_val, SMALL);        
        }
    }

    // Trộn thêm tổng chiều dài tệp vào mã băm cuối cùng
    hash_val ^= out_total_bytes; 
    hash_val *= PRIME;

    return hash_val; // Trả về mã băm 64-bit hoàn chỉnh
}

/*
 * Hàm intToHex: Chuyển đổi mã băm từ dạng số nguyên 64-bit sang dạng chuỗi Hex.
 */
string intToHex(u64 hash_val)
{
    stringstream ss; 
    ss << setfill('0') << setw(16) << hex << hash_val;
    return ss.str(); 
}

/*
 * Hàm testFile: Tạo file test
 */
void testFile(fs::path filePath){
    ofstream out_file(filePath.string(), ios::app); 
    if (out_file) {
        for (int i = 0; i < 1000000; ++i) { out_file << "Day la mot dong du lieu dai de test toc do bam.\n"; }
        cout << "Đã tạo file test\n";
        out_file.close();
    }
}

/*
 * Hàm main: Điểm bắt đầu (entry point) của chương trình.
 */
int main(int argc, char* argv[])
{
    // 1. Lấy đường dẫn tuyệt đối của chính file .exe đang chạy từ tham số argv[0]
    fs::path exePath = fs::absolute(fs::path(argv[0]));
    fs::path exeDir = exePath.parent_path();
    fs::path filePath = exeDir / "Hashing_Test.txt";

    // Mở tệp ở chế độ ios::binary (nhị phân) để đảm bảo đọc chính xác từng byte
    if (!fs::exists(filePath)) testFile(filePath);
    ifstream in_file(filePath.string(), ios::binary); 

    // Các biến để hứng kết quả thống kê từ hàm băm
    u64 total_bytes = 0;
    u64 total_blocks = 0;
    u64 read_count = 0;

    cout << "Đang băm khối 64-bit...\n";
    
    // *** GỌI HÀM BĂM VÀ ĐƯA CÁC BIẾN VÀO ĐỂ LẤY THỐNG KÊ ***
    u64 final_hash = hashingSuperFast(in_file, total_bytes, total_blocks, read_count); 
    
    in_file.close(); // Đóng tệp sau khi băm xong

    // In kết quả thống kê và mã băm ra màn hình
    cout << "--------------------------------------------------\n";
    cout << "THỐNG KÊ TỆP:\n";
    cout << "- Số byte / kí tự:     " << total_bytes << " bytes\n";
    cout << "- Số lần nạp buffer:   " << read_count << " lần\n";
    cout << "- Số khối 64-bit:      " << total_blocks << " khối\n";
    cout << "- Số byte lẻ:          " << (total_bytes % 8) << " bytes\n";
    cout << "--------------------------------------------------\n";
    cout << "KẾT QUẢ BĂM:\n";
    cout << "- Mã băm Int:          " << final_hash << "\n"; 
    cout << "- Mã băm Hex:          " << intToHex(final_hash) << "\n"; 
    cout << "--------------------------------------------------\n";

    return 0; // Kết thúc chương trình thành công
}