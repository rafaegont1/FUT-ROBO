#ifndef FILE_UTIL_HPP
#define FILE_UTIL_HPP

#include <vector>
#include <string>
#include <opencv2/opencv.hpp>

namespace FileUtil {

    // Reads a file containing an array of numbers. If the file is not found, returns an empty array.
    std::vector<float> file_read(const std::string& name);

    // Writes data to a file. If the folder doesn't exist, it will be created.
    void file_write(const std::string& name, const std::vector<float>& data);

} // namespace FileUtil

#endif // FILE_UTIL_HPP
