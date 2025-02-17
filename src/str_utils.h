#pragma once
// Copyright (c) 2021 Pastel Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <string>
#include <algorithm>

/**
 * trim string in-place from start (left trim).
 *
 * \param s - string to ltrim
 */
static inline void ltrim(std::string &s)
{
    s.erase(s.begin(), std::find_if(s.cbegin(), s.cend(), [](const auto ch) { return !std::isspace(ch); }));
}

/**
 * trim string in-place from end (right trim).
 *
 * \param s - string to rtrim
 */
static inline void rtrim(std::string& s)
{
    s.erase(std::find_if(s.crbegin(), s.crend(), [](const auto ch) { return !std::isspace(ch); }).base(), s.end());
}

/**
 * trim string in-place (both left & right trim).
 */
static inline void trim(std::string& s)
{
    ltrim(s);
    rtrim(s);
}

/**
 * lowercase string in-place.
 *
 * \param s
 */
static inline void lowercase(std::string &s)
{
    std::transform(s.cbegin(), s.cend(), s.begin(), [](const auto ch) { return std::tolower(ch); });
}

/**
 * uppercase string in-place.
 *
 * \param s
 */
static inline void uppercase(std::string& s)
{
    std::transform(s.cbegin(), s.cend(), s.begin(), [](const auto ch) { return std::toupper(ch); });
}

static inline void replaceAll(std::string &s, const std::string& sFrom, const std::string &sTo)
{
    size_t nPos = 0;
    while ((nPos = s.find(sFrom, nPos)) != std::string::npos)
    {
        s.replace(nPos, sFrom.length(), sTo);
        nPos += sTo.length();
    }
}

static inline bool isalphaex(const char c) noexcept
{
    return ((c >= 'A') && (c <= 'Z')) || ((c >= 'a') && (c <= 'z'));
}
static inline bool isdigitex(const char c) noexcept
{
    return (c >= '0') && (c <= '9');
}